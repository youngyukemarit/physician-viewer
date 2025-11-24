import streamlit as st
import pandas as pd
import json

st.set_page_config(
    page_title="Physician Profile Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")

    # Parse JSON fields safely
    json_cols = ["work_experience", "residency", "medical_school", "emails", "insurance"]

    for col in json_cols:
        def safe_parse(val):
            if pd.isna(val) or val.strip() == "" or val.strip() == "[]":
                return []
            try:
                return json.loads(val)
            except:
                return []

        df[col] = df[col].apply(safe_parse)

    return df

df = load_data()

# -----------------------------
# Sidebar Selector
# -----------------------------
st.sidebar.title("Select Physician")

names = sorted(df["full_name"].unique())
selected_name = st.sidebar.selectbox(
    "Choose a physician:",
    names,
    index=0,
)

row = df[df["full_name"] == selected_name].iloc[0]

# -----------------------------
# Page Title
# -----------------------------
st.markdown(f"# {selected_name}")

# -----------------------------
# Helper Renderers
# -----------------------------
def render_experience(items):
    if not items:
        st.write("N/A")
        return
    for item in items:
        employer = item.get("employer", "N/A")
        role = item.get("role", "N/A")
        start = item.get("start", "N/A")
        end = item.get("end", "N/A")
        location = item.get("location", "")
        st.markdown(f"**{employer} — {role}**")
        st.write(f"{start} → {end}")
        if location:
            st.write(location)
        links = item.get("source", [])
        for l in links:
            st.markdown(f"- [{l}]({l})")
        st.write("---")


def render_school(items):
    if not items:
        st.write("N/A")
        return
    for item in items:
        inst = item.get("institution", "N/A")
        start = item.get("start_year", "N/A")
        end = item.get("end_year", "N/A")
        st.markdown(f"**{inst}**")
        st.write(f"{start} → {end}")

        links = item.get("source", [])
        for l in links:
            st.markdown(f"- [{l}]({l})")
        st.write("---")


# -----------------------------
# 3 Column Layout
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧑‍⚕️ Work Experience")
    render_experience(row.work_experience)

with col2:
    st.subheader("🏥 Residency")
    render_school(row.residency)

with col3:
    st.subheader("🎓 Medical School")
    render_school(row.medical_school)

# -----------------------------
# Additional Details
# -----------------------------
st.write("---")
st.subheader("Additional Details")

npi = str(row["npi"])
dox = row.get("doximity_url", "N/A")
linkedin = row.get("linkedin_url", "N/A")

# Emails
emails = row.emails if isinstance(row.emails, list) else []
ins = row.insurance if isinstance(row.insurance, list) else []

colA, colB, colC, colD = st.columns(4)

with colA:
    st.markdown("**NPI**")
    st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/registry/npi/{npi})")

with colB:
    st.markdown("**Doximity**")
    if isinstance(dox, str) and dox.startswith("http"):
        st.markdown(f"[{dox}]({dox})")
    else:
        st.write("N/A")

with colC:
    st.markdown("**LinkedIn**")
    if isinstance(linkedin, str) and linkedin.startswith("http"):
        st.markdown(f"[{linkedin}]({linkedin})")
    else:
        st.write("N/A")

with colD:
    st.markdown("**Emails & Insurance**")

    if emails:
        st.write("**Emails:**")
        for e in emails:
            st.write(f"- {e.get('email', 'N/A')}")
    else:
        st.write("Emails: N/A")

    st.write("")
    if ins:
        st.write("**Insurance:**")
        for i in ins:
            st.write(f"- {i.get('insurance', 'N/A')}")
    else:
        st.write("Insurance: N/A")
