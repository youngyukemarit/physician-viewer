import streamlit as st
import pandas as pd
import json

# ---------------------------------------
# Load Data
# ---------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("/mnt/data/enrichment_clean.csv")

    # JSON columns to parse (based on your actual CSV)
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
        if pd.isna(x) or x.strip() == "":
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

# Sort list alphabetically
physician_list = sorted(df["cleaned.full_name"].fillna("Unknown").tolist())

# Dropdown selector
selected_name = st.selectbox(
    "Select a physician",
    physician_list
)

# Get row
row = df[df["cleaned.full_name"] == selected_name].iloc[0]

# ---------------------------------------
# Helper renders
# ---------------------------------------

def render_section(title, items, fields):
    """Render a list of dictionaries with specific fields"""
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

# ---------------- COL 1 — MAIN PROFILE ----------------

with col1:
    st.header(row["cleaned.full_name"])

    # NPI Link
    npi_val = row["npi"]
    if pd.notna(npi_val) and str(npi_val).isdigit():
        st.markdown(f"**NPI:** [{npi_val}](https://npiregistry.cms.hhs.gov/registry-details/{npi_val})")
    else:
        st.markdown("**NPI:** N/A")

    st.subheader("Work Experience")
    render_section(
        "Work Experience",
        row["cleaned.work_experience"],
        {"Employer": "employer", "Role": "role", "Location": "location"}
    )

# ---------------- COL 2 — TRAINING ----------------

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

# ---------------- COL 3 — OTHER DETAILS ----------------

with col3:

    # Years experience
    st.markdown("### **Years Experience**")
    yv = row.get("cleaned.years_experience.value", "N/A")
    st.write(yv if pd.notna(yv) else "N/A")

    # Emails
    render_simple_list("Emails", row["cleaned.emails"])

    # Insurance
    render_simple_list("Insurance Accepted", row["cleaned.insurance_accepted"])

    # LinkedIn
    link_url = row.get("cleaned.linkedin_url.url", "")
    if isinstance(link_url, str) and link_url.startswith("http"):
        st.markdown(f"### LinkedIn\n[{link_url}]({link_url})")
    else:
        st.markdown("### LinkedIn\nN/A")

    # Doximity
    dox_url = row.get("cleaned.doximity_url.url", "")
    if isinstance(dox_url, str) and dox_url.startswith("http"):
        st.markdown(f"### Doximity\n[{dox_url}]({dox_url})")
    else:
        st.markdown("### Doximity\nN/A")
