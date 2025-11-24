import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide", page_title="Physician Profiles")

# -----------------------------
# Load + Safe-Parse Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")

    # Identify columns that contain JSON-like strings
    json_cols = [
        "work_experience",
        "residency",
        "medical_school",
        "emails",
        "insurance"
    ]

    def safe_parse(val):
        if pd.isna(val) or val == "" or val == "N/A":
            return None
        try:
            return json.loads(val)
        except:
            return None

    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    return df


df = load_data()

# -----------------------------
# Sidebar: Dropdown Selector
# -----------------------------
st.sidebar.title("Select Physician")
names = df["full_name"].tolist()
selected_name = st.sidebar.selectbox("Choose a physician:", names)

# Get row
row = df[df["full_name"] == selected_name].iloc[0]

st.title(selected_name)

# -----------------------------
# Render Sections
# -----------------------------
def render_section(title, records, icon=""):
    st.subheader(f"{icon} {title}")

    if not records:
        st.write("N/A")
        return

    for item in records:
        employer = item.get("employer", "N/A")
        role = item.get("role", "N/A")
        start = item.get("start", "N/A")
        end = item.get("end", "N/A")
        location = item.get("location", "N/A")
        sources = item.get("source", [])

        st.markdown(f"**{employer} — {role}**")
        st.write(f"{start} → {end}")
        st.write(location)

        if sources:
            for s in sources:
                st.markdown(f"- [{s}]({s})")
        st.markdown("---")


# 3-column layout
col1, col2, col3 = st.columns(3)

with col1:
    render_section("Work Experience", row.get("work_experience"), "💼")

with col2:
    render_section("Residency", row.get("residency"), "🧑‍⚕️")

with col3:
    render_section("Medical School", row.get("medical_school"), "🎓")

# -----------------------------
# Additional Details
# -----------------------------
st.markdown("### Additional Details")

npi = row.get("npi", "N/A")
dox = row.get("doximity_url", "N/A")
linkedin = row.get("linkedin_url", "N/A")
emails = row.get("emails", None)
insurance = row.get("insurance", None)

colA, colB, colC, colD = st.columns(4)

with colA:
    st.write("**NPI**")
    if npi and npi != "N/A":
        st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/provider-view/{npi})")
    else:
        st.write("N/A")

with colB:
    st.write("**Doximity**")
    if isinstance(dox, str) and dox.startswith("http"):
        st.markdown(f"[{dox}]({dox})")
    else:
        st.write("N/A")

with colC:
    st.write("**LinkedIn**")
    if isinstance(linkedin, str) and linkedin.startswith("http"):
        st.markdown(f"[{linkedin}]({linkedin})")
    else:
        st.write("N/A")

with colD:
    st.write("**Emails & Insurance**")

    if emails:
        for e in emails:
            st.markdown(f"- {e.get('email', 'N/A')} ({e.get('type','')})")
    else:
        st.write("Emails: N/A")

    if insurance:
        for ins in insurance:
            st.markdown(f"- {ins.get('insurance','N/A')}")
    else:
        st.write("Insurance: N/A")
