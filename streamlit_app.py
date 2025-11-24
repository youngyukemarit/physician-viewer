import streamlit as st
import pandas as pd
import json

# ---------------------------------------
# Load Data
# ---------------------------------------
@st.cache_data
def load_data():
    # IMPORTANT: CSV must be in the same folder as this .py file
    df = pd.read_csv("enrichment_clean.csv")

    # JSON columns we need to parse
    json_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted",
        "cleaned.years_experience.source",
        "cleaned.linkedin_url.source",
        "cleaned.doximity_url.source",
    ]

    def try_parse(x):
        if pd.isna(x) or str(x).strip() == "":
            return []
        try:
            return json.loads(x)
        except:
            return []

    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(try_parse)

    return df

df = load_data()

# ---------------------------------------
# UI CONFIG
# ---------------------------------------
st.set_page_config(layout="wide")

st.title("📘 Physician Profile Viewer")

# Sort names alphabetically
physician_list = sorted(df["cleaned.full_name"].fillna("Unknown").tolist())

# Dropdown
selected_name = st.selectbox("Select a physician", physician_list)

# Get row
row = df[df["cleaned.full_name"] == selected_name].iloc[0]

# ---------------------------------------
# Helper functions
# ---------------------------------------
def render_section(title, items, fields):
    st.markdown(f"### **{title}**")

    if not isinstance(items, list) or len(items) == 0:
        st.markdown("_N/A_")
        return

    for idx, item in enumerate(items, start=1):
        st.markdown(f"**{idx}.**")
        for label, key in fields.items():
            val = item.get(key, "N/A")
            if val in [None, "", [], {}]:
                val = "N/A"
            st.write(f"- **{label}:** {val}")
        st.markdown("---")


def render_simple_list(title, lst):
    st.markdown(f"### **{title}**")
    if lst and isinstance(lst, list) and len(lst) > 0:
        for item in lst:
            st.write(f"- {item}")
    else:
        st.write("_N/A_")

# ---------------------------------------
# Layout
# ---------------------------------------
col1, col2, col3 = st.columns([1.2, 1, 1])

# === COL 1: BASIC INFO + WORK ===
with col1:
    st.header(row["cleaned.full_name"])

    # NPI
    npi_val = row.get("npi", "")
    if pd.notna(npi_val) and str(npi_val).isdigit():
        st.markdown(f"**NPI:** [{npi_val}](https://npiregistry.cms.hhs.gov/registry-details/{npi_val})")
    else:
        st.markdown("**NPI:** N/A")

    render_section(
        "Work Experience",
        row["cleaned.work_experience"],
        {"Employer": "employer", "Role": "role", "Location": "location"}
    )

# === COL 2: TRAINING ===
with col2:
    render_section(
        "Residency",
        row["cleaned.residency"],
        {"Institution": "institution", "Start": "start_year", "End": "end_year"}
    )

    render_section(
        "Medical School",
        row["cleaned.medical_school"],
        {"Institution": "institution", "Start": "start_year", "End": "end_year"}
    )

# === COL 3: MISC ===
with col3:

    st.markdown("### **Years Experience**")
    val = row.get("cleaned.years_experience.value", "N/A")
    st.write(val if pd.notna(val) else "N/A")

    render_simple_list("Emails", row["cleaned.emails"])
    render_simple_list("Insurance Accepted", row["cleaned.insurance_accepted"])

    # LinkedIn
    linkedin = row.get("cleaned.linkedin_url.url", "")
    if isinstance(linkedin, str) and linkedin.startswith("http"):
        st.markdown(f"### LinkedIn\n[{linkedin}]({linkedin})")
    else:
        st.markdown("### LinkedIn\nN/A")

    # Doximity
    dox = row.get("cleaned.doximity_url.url", "")
    if isinstance(dox, str) and dox.startswith("http"):
        st.markdown(f"### Doximity\n[{dox}]({dox})")
    else:
        st.markdown("### Doximity\nN/A")
