import streamlit as st
import pandas as pd
import base64
import json

@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_export.csv")
    json_cols = ["work_experience", "residency", "medical_school", "citations", "emails"]
    for col in json_cols:
        df[col] = df[col].apply(
            lambda x: json.loads(x) if isinstance(x, str) and (x.startswith("[") or x.startswith("{")) else []
        )
    return df

df = load_data()

st.set_page_config(page_title="Physician Profile Viewer", layout="centered")
st.title("🩺 Physician Profile Viewer")
st.write("Browse enriched physician profiles.")

names = df["full_name"].dropna().unique()
selection = st.sidebar.selectbox("Select a physician", names)

record = df[df["full_name"] == selection].iloc[0]

st.header(record["full_name"])
st.subheader("📌 Basic Info")
st.write(f"**NPI:** {record['NPI']}")
st.write(f"**State:** {record.get('state', '')}")
st.write(f"**Primary Taxonomy:** {record.get('primary_taxonomy', '')}")

st.subheader("💼 Work Experience")
if len(record["work_experience"]) > 0:
    for exp in record["work_experience"]:
        st.write(f"- {exp}")
else:
    st.write("_None found_")

st.subheader("🏥 Residency")
if len(record["residency"]) > 0:
    for item in record["residency"]:
        st.write(f"- {item}")
else:
    st.write("_None found_")

st.subheader("🎓 Medical School")
if isinstance(record["medical_school"], dict) and len(record["medical_school"]) > 0:
    for k, v in record["medical_school"].items():
        st.write(f"- **{k}:** {v}")
else:
    st.write("_None found_")

st.subheader("📧 Emails")
if len(record["emails"]) > 0:
    for email in record["emails"]:
        st.write(f"- {email}")
else:
    st.write("_No emails found_")

st.subheader("🔗 Source Citations")
if len(record["citations"]) > 0:
    for url in record["citations"]:
        st.write(f"- [{url}]({url})")
else:
    st.write("_No source URLs found_")
