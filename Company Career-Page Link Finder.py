# career_links_finder.py
import re
import time
import pandas as pd
import streamlit as st
from googlesearch import search  # pip install googlesearch-python

st.set_page_config(page_title="Career-Page Link Finder", layout="wide")
st.title("🔗 Company Career-Page Link Finder")

# ──────────────────────────────────────────────────────────────
# 1.  Edit this list or read it from a file as you prefer
# ──────────────────────────────────────────────────────────────
COMPANIES = [
    "Apple", "Microsoft", "NVIDIA", "Amazon", "Alphabet (Google)", "Saudi Aramco",
    "Meta Platforms (Facebook)", "Berkshire Hathaway", "Broadcom", "TSMC", "Tesla",
    "Walmart", "Eli Lilly", "JPMorgan Chase", "Visa", "Tencent", "Mastercard",
    "Exxon Mobil", "Netflix", "Costco", "UnitedHealth", "Procter & Gamble", "Oracle",
    "Johnson & Johnson", "Home Depot", "SAP", "ICBC", "Coca-Cola", "AbbVie",
    "Bank of America", "T-Mobile US", "LVMH", "Alibaba", "Hermès", "Novo Nordisk",
    "Nestlé", "Kweichow Moutai", "Philip Morris International", "ASML", "Samsung",
    "Agricultural Bank of China", "Roche", "Salesforce", "Chevron",
    "International Holding Company", "Toyota", "Palantir", "IBM", "L'Oréal",
    "China Mobile", "McDonald’s", "Cisco", "Wells Fargo", "Abbott Laboratories",
    "China Construction Bank", "Novartis", "Linde", "AstraZeneca", "Bank of China",
    "General Electric", "Reliance Industries", "Merck", "Prosus", "HSBC", "PepsiCo",
    "Shell", "PetroChina", "AT&T", "American Express", "Morgan Stanley",
    "HDFC Bank", "Accenture", "Fomento Económico Mexicano", "Intuitive Surgical",
    "Deutsche Telekom", "Verizon", "Siemens", "Commonwealth Bank",
    "Thermo Fisher Scientific", "Inditex", "ServiceNow", "Intuit", "Goldman Sachs",
    "Royal Bank of Canada", "Blackstone Group", "RTX", "Walt Disney", "Xiaomi",
    "Qualcomm", "Uber", "Unilever", "Booking Holdings (Booking.com)", "Allianz SE",
    "Progressive", "BYD", "Adobe", "Amgen", "Sony", "AMD", "Boston Scientific"
]

# ──────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────
def looks_like_career_url(url: str) -> bool:
    """Heuristically decide whether a URL is a careers page."""
    return bool(re.search(r"(careers?|jobs?|work-with-us|join-us|employment)", url, re.I))


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_career_links(companies):
    """Search Google and return a DataFrame of company → career link."""
    records = []
    for company in companies:
        query = f"{company} careers"
        result_url = None

        # googlesearch-python current signature: search(query, num_results=10)
        for url in search(query, num_results=10):
            if looks_like_career_url(url):
                result_url = url
                break

        records.append({"company": company, "career_page": result_url or "NOT FOUND"})
        time.sleep(1)  # courtesy delay

    return pd.DataFrame(records)

# ──────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────
if st.button("🔍 Fetch Career Links"):
    with st.spinner("Searching Google… please wait"):
        df = fetch_career_links(COMPANIES)

    found = df["career_page"].ne("NOT FOUND").sum()
    st.success(f"Found links for {found} of {len(df)} companies.")

    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        file_name="company_career_links.csv",
        mime="text/csv"
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("Click the button to fetch the career-page links.")
