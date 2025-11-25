import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer", layout="wide")

# ---------- Helpers ----------
def safe_parse(x):
    if pd.isna(x) or x == "" or x == "N/A":
        return []
    try:
        return ast.literal_eval(x)
    except:
        return []

def safe_str(x):
    if pd.isna(x) or x == "" or x == "N/A":
        return "N/A"
    return str(x)

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Parse JSON fields
    json_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted"
    ]
    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    return df

df = load_data()

# ---------------- UI ----------------
st.title("📘 Physician Profile Viewer")
st.write("Select a physician to view enrichment results.")

# Physician dropdown (use cleaned.name)
physician_list = sorted(df["cleaned.name"].fillna("Unknown").tolist())

selected_name = st.selectbox("Choose Physician:", physician_list)

row = df[df["cleaned.name"] == selected_name].iloc[0]

st.header(selected_name)

# ------------- 3 COLS -------------
col1, col2, col3 = st.columns(3)

# ---- Work Experience ----
with col1:
    st.subheader("💼 Work Experience")
    we = row["cleaned.work_experience"]
    if not we:
        st.write("N/A")
    else:
        for item in we:
            employer = item.get("employer", "N/A")
            role = item.get("role", "N/A")
            start = item.get("start", "N/A")
            end = item.get("end", "N/A")
            loc = item.get("location", "")
            st.write(f"**{employer} — {role}**")
            st.write(f"{start} → {end}")
            if loc:
                st.write(loc)
            for src in item.get("source", []):
                st.write(f"- [{src}]({src})")
            st.write("---")

# ---- Residency ----
with col2:
    st.subheader("👨‍⚕️ Residency")
    res = row["cleaned.residency"]
    if not res:
        st.write("N/A")
    else:
        for item in res:
            inst = item.get("institution", "N/A")
            start = item.get("start_year", "N/A")
            end = item.get("end_year", "N/A")
            st.write(f"**{inst}**")
            st.write(f"{start} → {end}")
            for src in item.get("source", []):
                st.write(f"- [{src}]({src})")
            st.write("---")

# ---- Medical School ----
with col3:
    st.subheader("🎓 Medical School")
    ms = row["cleaned.medical_school"]
    if not ms:
        st.write("N/A")
    else:
        for item in ms:
            inst = item.get("institution", "N/A")
            start = item.get("start_year", "N/A")
            end = item.get("end_year", "N/A")
            st.write(f"**{inst}**")
            st.write(f"{start} → {end}")
            for src in item.get("source", []):
                st.write(f"- [{src}]({src})")
            st.write("---")

# ---------------- Details Section ----------------
st.markdown("---")
st.subheader("Details")

npi = safe_str(row["cleaned.npi"])
emails = row["cleaned.emails"]
insurance = row["cleaned.insurance_accepted"]
linkedin = safe_str(row.get("cleaned.linkedin_url.url", "N/A"))
dox = safe_str(row.get("cleaned.doximity_url.url", "N/A"))

st.write(f"**NPI:** [{npi}](https://npiregistry.cms.hhs.gov/provider-view/{npi})")

st.write("**Emails:**")
if emails:
    for item in emails:
        e = item.get("email", "N/A")
        st.write(f"- {e}")
else:
    st.write("N/A")

st.write("**Insurance:**")
if insurance:
    for item in insurance:
        s = item.get("insurance", "N/A")
        st.write(f"- {s}")
else:
    st.write("N/A")

st.write("**LinkedIn:**")
st.write(linkedin if linkedin != "N/A" else "N/A")

st.write("**Doximity:**")
st.write(dox if dox != "N/A" else "N/A")
