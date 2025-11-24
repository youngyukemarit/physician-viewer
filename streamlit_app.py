import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Viewer", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")
    return df

df = load_data()

# Convert stringified lists/dicts to real Python objects
def safe_parse(x):
    if pd.isna(x) or x == "" or x == "[]":
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

# Sidebar list
st.sidebar.title("Physicians")
phys_names = sorted(df["full_name"].unique())
selected_name = st.sidebar.selectbox("Select", phys_names)

record = df[df["full_name"] == selected_name].iloc[0]

st.title("👨‍⚕️ Physician Profile Viewer")
st.subheader(selected_name)

# ===========================
# BASIC INFO
# ===========================
st.markdown("## 🧾 Basic Info")

st.write(f"**NPI:** {record['NPI']}")
st.write(f"**State:** {record['state']}")
st.write(f"**Primary Taxonomy:** {record.get('primary_taxonomy', '')}")

# ===========================
# WORK EXPERIENCE
# ===========================
st.markdown("## 🏢 Work Experience")

we = record["work_experience"]

if len(we) == 0:
    st.write("No work experience found.")
else:
    for entry in we:
        st.markdown(f"**{entry.get('employer','')}** — *{entry.get('role','')}*")
        st.write(f"{entry.get('location','')}  \n{entry.get('start','')} → {entry.get('end','')}")
        sources = entry.get("source", [])
        if sources:
            st.write("Sources:")
            for s in sources:
                st.markdown(f"- [{s}]({s})")
        st.markdown("---")

# ===========================
# RESIDENCY
# ===========================
st.markdown("## 🏥 Residency")

res = record["residency"]
if len(res) == 0:
    st.write("No residency info found.")
else:
    for r in res:
        st.markdown(f"**{r.get('institution','')}**  \n{r.get('start_year','')} → {r.get('end_year','')}")
        for s in r.get("source", []):
            st.markdown(f"- [{s}]({s})")
        st.markdown("---")

# ===========================
# MEDICAL SCHOOL
# ===========================
st.markdown("## 🎓 Medical School")

ms = record["medical_school"]
if len(ms) == 0:
    st.write("No medical school info found.")
else:
    for m in ms:
        st.markdown(f"**{m.get('institution','')}**")
        st.write(f"{m.get('start_year','')} → {m.get('end_year','')}")
        for s in m.get("source", []):
            st.markdown(f"- [{s}]({s})")
        st.markdown("---")

# ===========================
# EMAILS
# ===========================
st.markdown("## ✉️ Emails")

emails = record["emails"]
if len(emails) == 0:
    st.write("No emails found.")
else:
    for e in emails:
        st.write(f"- {e}")

# ===========================
# INSURANCE ACCEPTED
# ===========================
st.markdown("## 🛡 Insurance Accepted")

ins = record["insurance_accepted"]
if len(ins) == 0:
    st.write("No insurance info found.")
else:
    for i in ins:
        st.write(f"- {i.get('insurance','')}")

# ===========================
# LINKS
# ===========================
st.markdown("## 🔗 Links")

if pd.notna(record.get("linkedin_url")) and record["linkedin_url"] not in ["", "N/A"]:
    st.markdown(f"- [LinkedIn]({record['linkedin_url']})")

if pd.notna(record.get("doximity_url")) and record["doximity_url"] not in ["", "N/A"]:
    st.markdown(f"- [Doximity]({record['doximity_url']})")
