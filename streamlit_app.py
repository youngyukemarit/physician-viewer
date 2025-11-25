import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Parse JSON-like list columns
    list_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted",
    ]

    def safe_parse(x):
        if pd.isna(x) or str(x).strip() in ["", "nan", "None"]:
            return []
        try:
            return ast.literal_eval(x)
        except Exception:
            return []

    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    return df


df = load_data()

# -----------------------------
# Sidebar / Selector
# -----------------------------
st.title("📘 Physician Profile Viewer")

# Build list of names for dropdown
if "cleaned.name" in df.columns:
    dropdown_options = df["cleaned.name"].tolist()
else:
    dropdown_options = df["raw.name"].tolist()

selected_name = st.selectbox("Choose Physician:", dropdown_options)

row = df[df["cleaned.name"] == selected_name].iloc[0]

# -----------------------------
# Helper functions
# -----------------------------
def render_list(items):
    if not items:
        return "N/A"
    out = ""
    for it in items:
        if isinstance(it, dict):
            out += f"- " + ", ".join([f"**{k.capitalize()}**: {v}" for k, v in it.items() if v]) + "\n"
        else:
            out += f"- {it}\n"
    return out

def render_links(items):
    if not items:
        return "N/A"
    out = ""
    for it in items:
        if isinstance(it, str) and it.startswith("http"):
            out += f"- [{it}]({it})\n"
        elif isinstance(it, dict):
            for v in it.values():
                if isinstance(v, str) and v.startswith("http"):
                    out += f"- [{v}]({v})\n"
    return out if out else "N/A"

# -----------------------------
# PAGE LAYOUT
# -----------------------------
name = row["cleaned.name"]
npi = str(row["cleaned.npi"])

work = row["cleaned.work_experience"]
residency = row["cleaned.residency"]
school = row["cleaned.medical_school"]
emails = row["cleaned.emails"]
insurance = row["cleaned.insurance_accepted"]
linkedin = row.get("cleaned.linkedin_url.url", "N/A")
dox = row.get("cleaned.doximity_url.url", "N/A")

st.header(name)

# 3 column layout for sections
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.subheader("💼 Work Experience")
    st.markdown(render_list(work))

with col2:
    st.subheader("👨‍⚕️ Residency")
    st.markdown(render_list(residency))

with col3:
    st.subheader("🎓 Medical School")
    st.markdown(render_list(school))

st.markdown("---")
st.subheader("Details")

# -----------------------------
# FIXED NPI LINK  ✔✔✔
# -----------------------------
st.write(f"**NPI:** [{npi}](https://npiregistry.cms.hhs.gov/provider/{npi})")

# Emails
if emails and isinstance(emails, list):
    st.write("**Emails:**")
    st.markdown(render_links(emails))
else:
    st.write("**Emails:** N/A")

# Insurance  
st.write("**Insurance:**")
st.markdown(render_list(insurance))

# Doximity  
if isinstance(dox, str) and dox.startswith("http"):
    st.write(f"**Doximity:** [{dox}]({dox})")
else:
    st.write("**Doximity:** N/A")

# LinkedIn  
if isinstance(linkedin, str) and linkedin.startswith("http"):
    st.write(f"**LinkedIn:** [{linkedin}]({linkedin})")
else:
    st.write("**LinkedIn:** N/A")
