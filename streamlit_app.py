import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Viewer", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")
    return df

df = load_data()

def safe_parse(x):
    if pd.isna(x) or x == "" or x == "[]" or x == "{}":
        return []
    try:
        return ast.literal_eval(x)
    except:
        return []

df["work_experience"] = df["work_experience"].apply(safe_parse)
df["residency"] = df["residency"].apply(safe_parse)
df["medical_school"] = df["medical_school"].apply(safe_parse)
df["insurance_accepted"] = df["insurance_accepted"].apply(safe_parse)
df["emails"] = df["emails"].apply(safe_parse)

# Sorted physician list
physicians = sorted(df["full_name"].tolist())

# Sidebar full list
st.sidebar.title("Physicians")
selected_name = st.sidebar.radio("Select a physician:", physicians)

# Determine index for Next/Prev navigation
index = physicians.index(selected_name)

# Navigation buttons (top-right)
col_prev, col_next = st.columns([0.85, 0.15])

with col_next:
    if st.button("➡️ Next"):
        next_index = (index + 1) % len(physicians)
        selected_name = physicians[next_index]

with col_prev:
    if st.button("⬅️ Prev"):
        prev_index = (index - 1) % len(physicians)
        selected_name = physicians[prev_index]

# Reload record after any navigation change
record = df[df["full_name"] == selected_name].iloc[0]

# --- PAGE HEADER ---
st.title(f"👨‍⚕️ {selected_name}")

# 2-column layout
col1, col2 = st.columns([1.2, 1])

# ===========================
# BASIC INFO CARD
# ===========================
with col1:
    st.subheader("🧾 Basic Info")
    st.markdown(f"**NPI:** [{record['NPI']}](https://npiregistry.cms.hhs.gov/registry/NPI/{record['NPI']})")
    st.write(f"**State:** {record['state']}")
    st.write(f"**Primary Taxonomy:** {record.get('primary_taxonomy', '')}")

# ===========================
# LINKS CARD
# ===========================
with col2:
    st.subheader("🔗 Links")
    if record.get("linkedin_url") not in ["", "N/A", None]:
        st.markdown(f"- **LinkedIn:** {record['linkedin_url']}")
    if record.get("doximity_url") not in ["", "N/A", None]:
        st.markdown(f"- **Doximity:** {record['doximity_url']}")

# ===========================
# WORK EXPERIENCE
# ===========================
st.markdown("---")
st.subheader("🏢 Work Experience")

we = record["work_experience"]
if not we:
    st.write("No work experience found.")
else:
    for entry in we:
        with st.container():
            st.markdown(f"### {entry.get('employer', '')}")
            st.write(f"**Role:** {entry.get('role','')}")
            st.write(f"**Location:** {entry.get('location','')}")
            st.write(f"**Years:** {entry.get('start','')} → {entry.get('end','')}")
            if entry.get("source"):
                st.write("Sources:")
                for s in entry["source"]:
                    st.markdown(f"- [{s}]({s})")
            st.markdown("---")

# ===========================
# RESIDENCY
# ===========================
st.subheader("🏥 Residency")

res = record["residency"]
if not res:
    st.write("No residency info found.")
else:
    for r in res:
        st.markdown(f"**{r.get('institution','')}**")
        st.write(f"{r.get('start_year','')} → {r.get('end_year','')}")
        for s in r.get("source", []):
            st.markdown(f"- [{s}]({s})")
        st.markdown("---")

# ===========================
# MEDICAL SCHOOL
# ===========================
st.subheader("🎓 Medical School")

ms = record["medical_school"]
if not ms:
    st.write("No medical school info found.")
else:
    for m in ms:
        st.markdown(f"**{m.get('institution','')}**")
        st.write(f"{m.get('start_year','')} → {m.get('end_year','')}")
        for s in m.get("source", []):
            st.markdown(f"- [{s}]({s})")
        st.markdown("---")

# ===========================
# EMAIL
# ===========================
st.subheader("✉️ Emails")

emails = record["emails"]
if not emails:
    st.write("No emails found.")
else:
    for e in emails:
        st.write(f"- {e}")

# ===========================
# INSURANCE
# ===========================
st.subheader("🛡 Insurance Accepted")

ins = record["insurance_accepted"]
if not ins:
    st.write("No insurance info found.")
else:
    for i in ins:
        st.write(f"- {i.get('insurance','')}")
