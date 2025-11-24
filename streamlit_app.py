import streamlit as st
import pandas as pd
import ast

# -------------------------
# Load data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Parse JSON-like columns safely
    def parse_json(x):
        if pd.isna(x) or x == "" or x == "[]":
            return []
        try:
            return ast.literal_eval(x)
        except:
            return []

    df["cleaned.work_experience"] = df["cleaned.work_experience"].apply(parse_json)
    df["cleaned.residency"] = df["cleaned.residency"].apply(parse_json)

    # medical school is a dict-like object
    def parse_dict(x):
        if pd.isna(x) or x == "" or x == "{}":
            return {}
        try:
            return ast.literal_eval(x)
        except:
            return {}

    df["cleaned.medical_school"] = df["cleaned.medical_school"].apply(parse_dict)

    # emails + insurance are lists
    df["cleaned.emails"] = df["cleaned.emails"].apply(parse_json)
    df["cleaned.insurance_accepted"] = df["cleaned.insurance_accepted"].apply(parse_json)

    return df


df = load_data()

# -------------------------------------------------------------------
#  UI SETUP
# -------------------------------------------------------------------

st.set_page_config(page_title="Physician Profiles", layout="wide")

st.title("📘 Physician Profile Viewer")

# Dropdown list of names
physician_list = sorted(df["cleaned.full_name"].fillna("Unknown").tolist())
selected_name = st.selectbox("Choose Physician", physician_list)

row = df[df["cleaned.full_name"] == selected_name].iloc[0]

# -------------------------------------------------------------------
#  MAIN LAYOUT
# -------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 1, 1])

# -------------------------
#  LEFT COLUMN — WORK EXPERIENCE
# -------------------------
with col1:
    st.subheader("🏥 Work Experience")
    work = row["cleaned.work_experience"]
    if not work:
        st.write("N/A")
    else:
        for job in work:
            employer = job.get("employer", "N/A")
            role = job.get("role", "N/A")
            years = job.get("years", "N/A")
            st.markdown(f"• **{role}** — {employer} ({years})")

# -------------------------
#  MIDDLE COLUMN — RESIDENCY
# -------------------------
with col2:
    st.subheader("🎓 Residency")
    residency = row["cleaned.residency"]
    if not residency:
        st.write("N/A")
    else:
        for r in residency:
            inst = r.get("institution", "N/A")
            year = r.get("year", "N/A")
            st.markdown(f"• **{inst}** ({year})")

# -------------------------
#  RIGHT COLUMN — MEDICAL SCHOOL
# -------------------------
with col3:
    st.subheader("🏫 Medical School")
    school = row["cleaned.medical_school"]
    if not school:
        st.write("N/A")
    else:
        name = school.get("name", "N/A")
        year = school.get("year", "N/A")
        st.markdown(f"**{name}** ({year})")

# -------------------------------------------------------------------
# BELOW: LINKS + EMAILS + INSURANCE
# -------------------------------------------------------------------
st.divider()
st.subheader("🔗 Profile Links & Details")

# NPI
npi = row["npi"]
st.markdown(f"**NPI:** [{npi}](https://npiregistry.cms.hhs.gov/provider-view/{npi})")

# LinkedIn
linkedin = row["cleaned.linkedin_url.url"]
if pd.notna(linkedin) and linkedin != "N/A":
    st.markdown(f"**LinkedIn:** [{linkedin}]({linkedin})")
else:
    st.write("**LinkedIn:** N/A")

# Doximity
dox = row["cleaned.doximity_url.url"]
if pd.notna(dox) and dox != "N/A":
    st.markdown(f"**Doximity:** [{dox}]({dox})")
else:
    st.write("**Doximity:** N/A")

# Emails
emails = row["cleaned.emails"]
if emails:
    st.markdown("**Emails:**<br>" + "<br>".join(emails), unsafe_allow_html=True)
else:
    st.write("**Emails:** N/A")

# Insurance
ins = row["cleaned.insurance_accepted"]
if ins:
    st.markdown("**Insurance Accepted:**<br>" + "<br>".join(ins), unsafe_allow_html=True)
else:
    st.write("**Insurance Accepted:** N/A")
