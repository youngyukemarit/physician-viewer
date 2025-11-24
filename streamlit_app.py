import streamlit as st
import pandas as pd
import ast
import json

# -----------------------------------
# Helper: pretty format a list of dicts
# -----------------------------------
def render_section(list_of_dicts, fields):
    if not list_of_dicts:
        st.write("N/A")
        return

    for item in list_of_dicts:
        with st.container():
            for label, key in fields:
                value = item.get(key, "N/A")
                if isinstance(value, list):
                    # for links or sources
                    for link in value:
                        st.markdown(f"- [{link}]({link})")
                else:
                    st.markdown(f"**{label}:** {value}")
            st.markdown("---")

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    json_cols = [
        "work_experience",
        "residency",
        "medical_school",
        "insurance",
        "emails"
    ]

    for col in json_cols:
        def safe_parse(x):
            if pd.isna(x) or x.strip() == "":
                return []
            try:
                return json.loads(x)
            except:
                try:
                    return ast.literal_eval(x)
                except:
                    return []
        df[col] = df[col].apply(safe_parse)

    return df

df = load_data()

# -----------------------------------
# UI
# -----------------------------------
st.title("📘 Physician Profile Viewer")

physicians = sorted(df["full_name"].tolist())
selected = st.selectbox("Choose Physician:", physicians)

row = df[df["full_name"] == selected].iloc[0]

# -----------------------------------
# Layout
# -----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👔 Work Experience")
    render_section(
        row["work_experience"],
        [
            ("Employer", "employer"),
            ("Role", "role"),
            ("Start", "start_year"),
            ("End", "end_year"),
            ("Location", "location"),
            ("Source", "source"),
        ]
    )

with col2:
    st.subheader("👨‍⚕️ Residency")
    render_section(
        row["residency"],
        [
            ("Institution", "institution"),
            ("Start Year", "start_year"),
            ("End Year", "end_year"),
            ("Source", "source"),
        ]
    )

with col3:
    st.subheader("🎓 Medical School")
    render_section(
        row["medical_school"],
        [
            ("Institution", "institution"),
            ("Start Year", "start_year"),
            ("End Year", "end_year"),
            ("Source", "source"),
        ]
    )

# -----------------------------------
# Additional Details
# -----------------------------------
st.markdown("---")
st.subheader("📄 Details")

st.markdown(f"**NPI:** {row['npi'] if pd.notna(row['npi']) else 'N/A'}")

# Emails
st.markdown("**Emails:**")
if row["emails"]:
    for email in row["emails"]:
        st.write(email.get("email", "N/A"))
else:
    st.write("N/A")

# Insurance
st.markdown("**Insurance:**")
if row["insurance"]:
    for ins in row["insurance"]:
        st.write(ins.get("insurance", "N/A"))
else:
    st.write("N/A")

# Doximity + LinkedIn
st.markdown("**Doximity:**")
if pd.notna(row.get("doximity_url", "")) and row["doximity_url"] != "":
    st.markdown(f"[{row['doximity_url']}]({row['doximity_url']})")
else:
    st.write("N/A")

st.markdown("**LinkedIn:**")
linkedin = row.get("linkedin_url", "")
if pd.notna(linkedin) and linkedin != "":
    st.markdown(f"[{linkedin}]({linkedin})")
else:
    st.write("N/A")
