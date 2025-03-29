import csv
from jobspy import scrape_jobs

# General IT search term
search_term_query = "Information Technology OR IT"

# Google-specific query
google_search_term_query = "entry level and mid level Information Technology jobs"

# Scrape jobs
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
    search_term=search_term_query,
    google_search_term=google_search_term_query,
    location="United States",
    results_wanted=500,
    hours_old=48,            # Jobs posted in the last 10 hours
    country_indeed='USA',
    job_type='fulltime',
    linkedin_fetch_description=True,
    verbose=2
)

# Print results to console
print(f"Found {len(jobs)} jobs.")
print(jobs.head())

# Save to CSV
jobs.to_csv(
    "jobs.csv",
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    index=False
)
