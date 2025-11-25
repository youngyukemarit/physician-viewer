import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer", layout="wide")

# -------------------------
# Load data
# -------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Columns that contain python-like lists or dicts
    complex_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted",
    ]

    def safe_parse(x):
        if pd.isna(x) or x in ["", "[]", "{}", "N/A"]:
            return []
        try:
            return ast.literal_eval(x)
        except:
            return []

    for c in complex_cols:
        df[c] = df[c].apply(safe_parse)

    return df

df = load_data()

# -------------------------
# UI Header
# -------------------------

st.title("📘 Physician Profile Viewer")
st.caption("Select a physician to view enrichment results.")

# Dropdown sorted by name
names = sorted(df["cleaned.name"].fillna("Unknown").tolist())
selected_name = st.selectbox("Choose Physician:", names)

row = df[df["cleaned.name"] == selected_name].iloc[0]

st.markdown(f"## {row['cleaned.name']}")

# -------------------------
# Section helpers
# -------------------------

def render_experience(items):
    if not items:
        st.write("N/A")
        return
    for item in items:
        employer = item.get("employer", "N/A")
        role = item.get("role", "N/A")
        start = item.get("start", "N/A")
        end = item.get("end", "N/A")
        location = item.get("location", "N/A")
        st.markdown(
            f"**{employer} — {role}**  \n"
            f"{start} → {end}  \n"
            f"{location}"
        )
        # Sources
        for src in item.get("source", []):
            st.markdown(f"- [{src}]({src})")
        st.markdown("---")

def render_education(items):
    if not items:
        st.write("N/A")
        return
    for item in items:
        inst = item.get("institution", "N/A")
        start = item.get("start_year", "N/A")
        end = item.get("end_year", "N/A")
        st.markdown(f"**{inst}**  \n{start} → {end}")
        for src in item.get("source", []):
            st.markdown(f"- [{src}]({src})")
        st.markdown("---")

# -------------------------
# Display 3 columns
# -------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💼 Work Experience")
    render_experience(row["cleaned.work_experience"])

with col2:
    st.subheader("👨‍⚕️ Residency")
    render_education(row["cleaned.residency"])

with col3:
    st.subheader("🎓 Medical School")
    render_education(row["cleaned.medical_school"])

# -------------------------
# Details Section
# -------------------------

st.markdown("---")
st.subheader("Details")

# NPI
npi = row["cleaned.npi"]
st.markdown(f"**NPI:** [{npi}](https://npiregistry.cms.hhs.gov/registry/{npi})")

# Emails
emails = row["cleaned.emails"]
if not emails:
    st.markdown("**Emails:** N/A")
else:
    st.markdown("**Emails:**")
    for e in emails:
        st.markdown(f"- {e.get('email')} ({e.get('type')})")

# Insurance
ins = row["cleaned.insurance_accepted"]
if not ins:
    st.markdown("**Insurance:** N/A")
else:
    st.markdown("**Insurance:**")
    for i in ins:
        ins_name = i.get("insurance", "N/A")
        st.markdown(f"- {ins_name}")

# Doximity
dox = row.get("cleaned.doximity_url.url", "N/A")
if pd.isna(dox) or dox in ["", "N/A"]:
    st.markdown("**Doximity:** N/A")
else:
    st.markdown(f"**Doximity:** [{dox}]({dox})")

# LinkedIn
linkedin = row.get("cleaned.linkedin_url.url", "N/A")
if pd.isna(linkedin) or linkedin in ["", "N/A"]:
    st.markdown("**LinkedIn:** N/A")
else:
    st.markdown(f"**LinkedIn:** [{linkedin}]({linkedin})")
