import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Viewer", layout="wide")

# =========================
# Load CSV
# =========================
@st.cache_data
def load_data():
    # IMPORTANT: This loads the CSV from your GitHub repo
    df = pd.read_csv("enrichment_clean.csv")

    # Columns with JSON-like strings
    json_cols = ["work_experience", "residency", "medical_school",
                 "emails", "insurance", "sources"]

    def parse_json(x):
        if pd.isna(x) or x == "":
            return None
        try:
            return ast.literal_eval(x)
        except:
            return None

    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_json)

    return df


df = load_data()

st.title("📘 Physician Profile Viewer")

# =========================
# Dropdown
# =========================
if "cleaned.full_name" not in df.columns:
    st.error("Column 'cleaned.full_name' not found in CSV. Please confirm CSV headers.")
    st.stop()

df = df.sort_values("cleaned.full_name")
names = df["cleaned.full_name"].fillna("Unknown").tolist()

selected_name = st.selectbox("Select a physician:", names)

row = df[df["cleaned.full_name"] == selected_name].iloc[0]

# =========================
# Render Helpers
# =========================
def section(title, content):
    st.subheader(title)
    if not content:
        st.write("N/A")
    else:
        for item in content:
            if isinstance(item, dict):
                st.write("• " + ", ".join(f"{k}: {v}" for k, v in item.items()))
            else:
                st.write("• " + str(item))

def link(label, url):
    if url and isinstance(url, str) and url.startswith("http"):
        st.write(f"**{label}:** [{url}]({url})")
    else:
        st.write(f"**{label}:** N/A")

# =========================
# Top 3 Columns
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    section("🧑‍⚕️ Work Experience", row.get("work_experience"))

with col2:
    section("🎓 Residency", row.get("residency"))

with col3:
    section("🏥 Education", row.get("medical_school"))

st.markdown("---")

# =========================
# Quick Details Row
# =========================
st.subheader("Quick Details")

npi = row.get("npi")
npi_link = (
    f"https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi}"
    if pd.notna(npi)
    else None
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    link("NPI", npi_link)

with c2:
    link("Doximity", row.get("doximity_url"))

with c3:
    link("LinkedIn", row.get("linkedin_url"))

with c4:
    st.write("**Emails:**")
    if row.get("emails"):
        for e in row.emails:
            st.write("•", e)
    else:
        st.write("N/A")

with c5:
    st.write("**Insurance:**")
    if row.get("insurance"):
        for ins in row.insurance:
            st.write("•", ins)
    else:
        st.write("N/A")

st.markdown("---")

# =========================
# Source Citations
# =========================
st.subheader("Source Citations")

if row.get("sources"):
    for source in row.sources:
        if isinstance(source, dict) and "url" in source:
            url = source["url"]
            if isinstance(url, str) and url.startswith("http"):
                st.write(f"• [{url}]({url})")
            else:
                st.write("• " + str(url))
        else:
            st.write("• " + str(source))
else:
    st.write("N/A")
