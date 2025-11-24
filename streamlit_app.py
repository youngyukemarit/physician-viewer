import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Physician Profiles", layout="wide")

# --------------------------
# Load & prepare the dataset
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")

    # Normalize JSON text → Python objects (lists/dicts)
    def parse_json(x):
        try:
            return json.loads(x) if isinstance(x, str) else x
        except:
            return None

    df["work_experience"] = df["work_experience"].apply(parse_json)
    df["residency"] = df["residency"].apply(parse_json)
    df["medical_school"] = df["medical_school"].apply(parse_json)
    df["emails"] = df["emails"].apply(parse_json)
    df["insurance_accepted"] = df["insurance_accepted"].apply(parse_json)

    # Sort alphabetically for dropdown list
    df = df.sort_values("full_name").reset_index(drop=True)

    return df

df = load_data()

# --------------------------
# Sidebar navigation
# --------------------------
st.sidebar.markdown("## Select Physician")

# Dropdown — taller menu
selected_name = st.sidebar.selectbox(
    "Choose a physician:",
    df["full_name"].tolist(),
    index=0,
    help="Scroll through the list (tall menu)"
)

# Current index
idx = df.index[df["full_name"] == selected_name][0]

# Previous / next navigation
col_prev, col_next = st.sidebar.columns(2)
if col_prev.button("⬅️ Prev"):
    idx = max(0, idx - 1)
if col_next.button("Next ➡️"):
    idx = min(len(df) - 1, idx + 1)

row = df.iloc[idx]

# Maintain dropdown sync when navigating
selected_name = row.full_name

# --------------------------
# UI LAYOUT
# --------------------------
st.markdown(f"# {row.full_name}")
st.markdown("---")

top_col1, top_col2 = st.columns([3, 1.5])

# --------------------------
# Column 1 – Main Profile Data
# --------------------------
with top_col1:

    # --- Work Experience ---
    st.subheader("Work Experience")
    we = row.work_experience

    if not we:
        st.write("N/A")
    else:
        for item in we:
            title = item.get("title", "N/A")
            org = item.get("organization", "N/A")
            years = item.get("years", "N/A")
            st.write(f"**{title}**, {org} — {years}")

    st.markdown("---")

    # --- Residency ---
    st.subheader("Residency")
    res = row.residency
    if not res:
        st.write("N/A")
    else:
        for item in res:
            program = item.get("program", "N/A")
            years = item.get("years", "N/A")
            st.write(f"{program} — {years}")

    st.markdown("---")

    # --- Medical School ---
    st.subheader("Medical School")
    ms = row.medical_school
    if not ms:
        st.write("N/A")
    else:
        name = ms.get("name", "N/A")
        year = ms.get("year", "N/A")
        st.write(f"{name} — {year}")

# --------------------------
# Column 2 – Side Info
# --------------------------
with top_col2:
    st.subheader("Quick Info")

    # NPI link
    npi_link = f"https://npiregistry.cms.hhs.gov/provider-view/{row.NPI}"
    st.markdown(f"**NPI:** [{row.NPI}]({npi_link})")

    # Doximity
    if isinstance(row.doximity_url, str) and row.doximity_url.strip():
        st.markdown(f"**Doximity:** [{row.doximity_url}]({row.doximity_url})")
    else:
        st.write("**Doximity:** N/A")

    # LinkedIn
    if isinstance(row.linkedin_url, str) and row.linkedin_url.strip():
        st.markdown(f"**LinkedIn:** [{row.linkedin_url}]({row.linkedin_url})")
    else:
        st.write("**LinkedIn:** N/A")

    # Emails
    st.subheader("Emails")
    emails = row.emails
    if not emails:
        st.write("N/A")
    else:
        for e in emails:
            st.write(f"- {e}")

    # Insurance
    st.subheader("Insurance Accepted")
    ins = row.insurance_accepted
    if not ins:
        st.write("N/A")
    else:
        for carrier in ins:
            st.write(f"- {carrier}")

st.markdown("---")
