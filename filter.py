from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pandas as pd
import streamlit as st
import os
import PyPDF2
from rake_nltk import Rake

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to get BERT embeddings
def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().numpy()

# Function to extract years of experience
def extract_experience(text):
    pattern = r'(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|work\s*experience|professional\s*experience|relevant\s*experience|in\s*(?:the\s*field|[a-zA-Z\s]*))?'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract keywords using RAKE
def extract_keywords(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()

# Save applied jobs
def save_applied_jobs(applied_jobs):
    applied_df = pd.DataFrame(applied_jobs)
    applied_df.to_csv('applied.csv', index=False)

def load_applied_jobs():
    if os.path.exists('applied.csv'):
        try:
            return pd.read_csv('applied.csv').to_dict('records')
        except pd.errors.EmptyDataError:
            return []
    return []

def main():
    st.title("All Job Listings (No Resume Required)")

    if 'applied_jobs' not in st.session_state:
        st.session_state.applied_jobs = load_applied_jobs()

    file_type = st.selectbox("Select resume file type", ["Markdown (MD)", "PDF"])
    uploaded_file = st.file_uploader("Upload your resume", type="md" if file_type == "Markdown (MD)" else "pdf")

    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file) if file_type == "PDF" else uploaded_file.read().decode('utf-8')
        st.write("Resume text extracted successfully!")

        jobs = pd.read_csv('jobs.csv')
        st.write(f"Loaded {len(jobs)} jobs.")
        jobs['description'] = jobs['description'].fillna('')

        filter_title = ['citizenship', 'senior', 'lead', 'Sr', '.Net', 'Clearance', 'Secret', 'Manager', 'Mgr', 'US Citizen', 'Principal', 'Embedded', 'HVAC', 'Staff']
        filter_description = ['citizenship', 'Clearance', 'Secret', 'TS/SCI', 'Citizen']
        filter_companies = ["Sreekar's company"]

        jobs = jobs[~(
            jobs['title'].str.contains('|'.join(filter_title), case=False, na=False) |
            jobs['description'].str.contains('|'.join(filter_description), case=False, na=False) |
            jobs['company'].str.contains('|'.join(filter_companies), case=False, na=False)
        )]

        jobs = jobs[jobs['location'].str.contains(',', na=False)]

        st.write(f"Remaining jobs: {len(jobs)}")

        resume_keywords = extract_keywords(resume_text)
        resume_experience = extract_experience(resume_text)

        similarity_method = st.radio("Select similarity method", ["BERT Embeddings + Cosine Similarity", "TF-IDF + Cosine Similarity"], index=1)

        if similarity_method == "BERT Embeddings + Cosine Similarity":
            resume_embedding = get_bert_embedding(' '.join(resume_keywords))

            if 'job_embeddings' not in st.session_state:
                st.session_state.job_embeddings = {}
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, (_, job) in enumerate(jobs.iterrows()):
                    job_text = job['title'] + ' ' + job['description']
                    job_keywords = extract_keywords(job_text)
                    st.session_state.job_embeddings[job['id']] = get_bert_embedding(' '.join(job_keywords))

                    progress = int((i + 1) / len(jobs) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Computing embeddings for job {i + 1} of {len(jobs)}...")

                st.write("BERT embeddings computed and cached!")

            similarity_scores = []
            for _, job in jobs.iterrows():
                job_embedding = st.session_state.job_embeddings[job['id']]
                job_experience = extract_experience(job['description'])
                bert_similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
                experience_match = 1 if resume_experience >= job_experience else 0
                final_score = bert_similarity * experience_match
                similarity_scores.append(final_score)

        else:
            all_keywords = [' '.join(resume_keywords)] + [
                ' '.join(extract_keywords(job['title'] + ' ' + job['description'])) for _, job in jobs.iterrows()
            ]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(all_keywords)
            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            similarity_scores = cosine_similarities

        jobs['similarity_score'] = similarity_scores
        threshold = st.slider("Set similarity threshold", 0.0, 1.0, 0.9)
        eligible_jobs = jobs[jobs['similarity_score'] > threshold]

        eligible_jobs['Apply'] = eligible_jobs['id'].apply(
            lambda job_id: job_id in [applied_job['id'] for applied_job in st.session_state.applied_jobs]
        )

        column_order = ['id', 'Apply', 'title', 'company', 'location', 'job_url', 'similarity_score', 'date_posted', 'company_num_employees']
        eligible_jobs = eligible_jobs[column_order]

        st.write(f"Found {len(eligible_jobs)} eligible jobs:")
        edited_df = st.data_editor(
            eligible_jobs,
            column_config={
                "Apply": st.column_config.CheckboxColumn("Apply", help="Check to apply to this job"),
                "job_url": st.column_config.LinkColumn("Job URL"),
            },
            hide_index=True,
        )

        if len(eligible_jobs) > 0:
            applied_job_ids = edited_df[edited_df['Apply']]['id'].tolist()
            st.session_state.applied_jobs = [
                {
                    'id': job['id'],
                    'title': job['title'],
                    'company': job['company'],
                    'job_url': job['job_url'],
                    'date_posted': job['date_posted'],
                    'similarity_score': job['similarity_score']
                }
                for job in eligible_jobs.to_dict('records') if job['id'] in applied_job_ids
            ]

        if st.button("Save Applied Jobs"):
            save_applied_jobs(st.session_state.applied_jobs)
            st.write("Applied jobs saved to `applied.csv`.")

        st.write("### Applied Jobs")
        if st.session_state.applied_jobs:
            applied_df = pd.DataFrame(st.session_state.applied_jobs)
            st.dataframe(applied_df, column_config={"job_url": st.column_config.LinkColumn()})
        else:
            st.write("No jobs applied yet.")

if __name__ == "__main__":
    main()
