import streamlit as st
import pandas as pd
import os

def main():
    st.title("All Job Listings (No Resume Required)")

    # Make sure jobs.csv exists in the same directory or provide a full path
    if not os.path.exists("jobs.csv"):
        st.error("jobs.csv not found. Please place it in the same directory as this script.")
        return

    # Load the jobs CSV
    jobs = pd.read_csv("jobs.csv")
    st.write(f"Loaded {len(jobs)} jobs.")

    # If 'description' column is missing or has NaNs, fill them with empty strings
    if 'description' in jobs.columns:
        jobs['description'] = jobs['description'].fillna('')
    else:
        # Create an empty column if you don't have 'description' at all
        jobs['description'] = ""

    # Example filters you can keep or remove:
    filter_title = [
        'citizenship', 'senior', 'lead', 'Sr',
        'Clearance', 'Secret', 'Manager', 'Mgr',
        'US Citizen', 'Principal', 'Embedded', 'HVAC', 'Staff'
    ]
    filter_description = [
        'citizenship', 'Clearance', 'Secret', 'TS/SCI', 'Citizen'
    ]
    filter_companies = ["Soham's company"]

    # Apply the filters
    jobs_filtered = jobs[~(
        jobs['title'].str.contains('|'.join(filter_title), case=False, na=False) |
        jobs['description'].str.contains('|'.join(filter_description), case=False, na=False) |
        jobs['company'].str.contains('|'.join(filter_companies), case=False, na=False)
    )]

    # Optional: only keep jobs that have a comma in the 'location' field
    # (the original code used this to filter out partial or empty location fields)
    if 'location' in jobs.columns:
        jobs_filtered = jobs_filtered[jobs_filtered['location'].str.contains(',', na=False)]

    st.write(f"Remaining jobs after filters: {len(jobs_filtered)}")

    # Show the filtered job listings
    # Adjust columns as desired
    columns_to_display = [
        'id', 'title', 'company', 'location', 'job_url',
        'date_posted', 'company_num_employees'
    ]
    # Filter the DataFrame to only those columns that exist
    valid_columns = [col for col in columns_to_display if col in jobs_filtered.columns]
    st.dataframe(jobs_filtered[valid_columns])

if __name__ == "__main__":
    main()
