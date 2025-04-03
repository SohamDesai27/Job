import streamlit as st
import pandas as pd
import imaplib
import email
from email.header import decode_header
import re

# -------------------------------
# Single-file Streamlit app
# -------------------------------

st.set_page_config(page_title="Email-Based Job Link Grabber", layout="wide")
st.title("💼 Job Links from Email Alerts (Indeed & Glassdoor)")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. IMAP EMAIL FETCHING LOGIC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fetch_job_links_from_email(
    email_user: str,
    email_pass: str,
    imap_server: str = "imap.gmail.com",
    folder: str = "INBOX"
):
    """
    Connects to the email account using IMAP, searches for Indeed/Glassdoor alerts,
    extracts job links from each matching email, and returns them as a list of URLs.
    """

    # Connect to the server via SSL
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_pass)

    # Select the mailbox you want to search
    mail.select(folder)

    # Search for emails from Indeed or Glassdoor
    # (this uses a basic IMAP search with an OR condition)
    status, data = mail.search(None, '(OR FROM "indeed.com" FROM "glassdoor.com")')
    if status != "OK":
        mail.close()
        mail.logout()
        return []

    mail_ids = data[0].split()  # A list of email IDs that match

    # Regex to find Indeed/Glassdoor job links inside email text or HTML
    job_link_pattern = re.compile(
        r'(https?://[^\s"]+indeed[^\s"]+|https?://[^\s"]+glassdoor[^\s"]+)'
    )

    all_job_links = []

    for mail_id in mail_ids:
        try:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Try to decode the email subject (for debugging/logging)
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

            # Walk through each part of the email to find the HTML/text
            links_found_in_email = []
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    # content_disposition = str(part.get("Content-Disposition"))  # not always needed
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except:
                        body = ""
                    links = job_link_pattern.findall(body)
                    links_found_in_email.extend(links)
            else:
                # For non-multipart emails
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                links = job_link_pattern.findall(body)
                links_found_in_email.extend(links)

            # Add links if any found
            if links_found_in_email:
                all_job_links.extend(links_found_in_email)

        except Exception as ex:
            # Optional: could log or print errors here
            print(f"Error parsing email ID {mail_id}: {ex}")

    # Close connection
    mail.close()
    mail.logout()

    # Remove duplicates
    unique_job_links = list(set(all_job_links))

    return unique_job_links

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. STREAMLIT UI
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Sidebar for user credentials
with st.sidebar:
    st.header("Email Credentials")
    user_email = st.text_input("Email Address", placeholder="you@gmail.com")
    user_password = st.text_input("App Password", type="password")
    st.write("""
    ⚠️ If using Gmail with 2FA, create an **App Password** in your Google account
    and use that here. Ensure IMAP is enabled in Gmail settings.
    """)

# Main button to fetch job links
if st.button("Fetch Job Links From Email"):
    if not user_email or not user_password:
        st.error("Please provide your email address and password/app password.")
    else:
        with st.spinner("Connecting to email and extracting links..."):
            try:
                job_links = fetch_job_links_from_email(
                    email_user=user_email,
                    email_pass=user_password,
                    imap_server="imap.gmail.com",
                    folder="INBOX"
                )
            except Exception as e:
                st.error(f"Error fetching job links: {e}")
                job_links = []

        # Once retrieved, display results
        if job_links:
            st.success(f"Found {len(job_links)} job links in your Indeed/Glassdoor emails!")

            # Convert to DataFrame
            jobs_df = pd.DataFrame({"job_url": job_links})

            # Example filtering: maybe only keep ones that mention 'devops' or 'DevOps' in the URL
            devops_df = jobs_df[jobs_df["job_url"].str.lower().str.contains("devops")]

            st.subheader("All Job Links")
            st.dataframe(jobs_df, use_container_width=True)

            # Display DevOps subset
            st.subheader("Possible 'DevOps' Links")
            st.dataframe(devops_df, use_container_width=True)

            # Download buttons
            st.download_button(
                "Download All Links CSV",
                data=jobs_df.to_csv(index=False),
                file_name="all_job_links.csv"
            )
            st.download_button(
                "Download DevOps Links CSV",
                data=devops_df.to_csv(index=False),
                file_name="devops_job_links.csv"
            )
        else:
            st.warning("No matching job links found in your Indeed/Glassdoor emails.")

else:
    st.info("Enter your email credentials in the sidebar and click the button to fetch job links.")
