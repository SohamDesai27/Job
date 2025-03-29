import csv
from jobspy import scrape_jobs

# Build a single OR string for the search_term
# We'll include "entry level DevOps engineer" plus all the other job titles you listed:
search_term_query = (
    "entry level DevOps engineer OR "
    "Software OR "
    "'Systems Administrator' OR "
    "DevOps OR "
    "'Database Administrator' OR "
    "SRE OR "
    "Infrastructure OR "
    "Platform OR "
    "'Technical Operations' OR "
    "'Technical product owner' OR "
    "'Data and reporting systems' OR "
    "'Data and systems' OR "
    "'Configuration/Release engineer' OR "
    "Orchestration OR "
    "Solutions OR "
    "'IT systems engineer' OR "
    "'IT analyst' OR "
    "'Systems verification software engineer' OR "
    "'Product Engineer' OR "
    "'Security Engineer' OR "
    "'Application Engineer'"
)

# Similarly for Google Jobs:
google_search_term_query = (
    "entry level and mid level DevOps engineer jobs OR "
    "Software OR "
    "'Systems Administrator' OR "
    "DevOps OR "
    "'Database Administrator' OR "
    "SRE OR "
    "Infrastructure OR "
    "Platform OR "
    "'Technical Operations' OR "
    "'Technical product owner' OR "
    "'Data and reporting systems' OR "
    "'Data and systems' OR "
    "'Configuration/Release engineer' OR "
    "Orchestration OR "
    "Solutions OR "
    "'IT systems engineer' OR "
    "'IT analyst' OR "
    "'Systems verification software engineer' OR "
    "'Product Engineer' OR "
    "'Security Engineer' OR "
    "'Application Engineer'"
)

# Now call scrape_jobs with these combined queries
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
    search_term=search_term_query,
    google_search_term=google_search_term_query,
    location="United States",
    results_wanted=500,
    hours_old=10,            # Last 10 hours
    country_indeed='USA',
    job_type='fulltime',
    linkedin_fetch_description=True,  # Slower, but fetches job descriptions + direct URLs
    # proxies=["..."],  # If you have proxies, specify them here to avoid blocking
    verbose=2
)

# Print results to console
print(f"Found {len(jobs)} jobs.")
print(jobs.head())

# Save results to CSV
jobs.to_csv(
    "jobs.csv",
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    index=False
)
