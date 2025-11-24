import streamlit as st
import pandas as pd

# -------------------------------
# Load CSV
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("profile_enrichment_base44.csv")

df = load_data()

# Ensure consistent types
def safe_list(x):
    if pd.isna(x) or x == "":
        return []
    try:
        return eval(x)
    except:
        return []

def safe_str(x):
    return "" if pd.isna(x) else str(x)

df["work_experience"] = df["work_experience"].apply(safe_list)
df["residency"] = df["residency"].apply(safe_list)
df["medical_school"] = df["medical_school"].apply(safe_list)
df["emails"] = df["emails"].apply(safe_list)
df["insurance_accepted"] = df["insurance_accepted"].apply(safe_list)


# -------------------------------
# Streamlit Layout
# -------------------------------
st.set_page_config(layout="wide", page_title="Physician Viewer")

st.markdown(
    "<h1 style='margin-bottom:0;'>Physician Profile Viewer</h1>",
    unsafe_allow_html=True,
)

# Sort by name for predictable ordering
names = sorted(df["full_name"].unique())

# Sidebar list (clickable, no radio button)
st.sidebar.markdown("### Physicians")
selected_name = st.sidebar.selectbox("", names, label_visibility="collapsed")

row = df[df["full_name"] == selected_name].iloc[0]

# Determine index for navigation
current_index = names.index(selected_name)

col_prev, col_next = st.columns([0.8, 0.2])
with col_next:
    if current_index < len(names) - 1:
        if st.button("Next →"):
            st.session_state["selected_name"] = names[current_index + 1]
with col_prev:
    if current_index > 0:
        if st.button("← Prev"):
            st.session_state["selected_name"] = names[current_index - 1]

# Handle navigation persistence
if "selected_name" in st.session_state:
    selected_name = st.session_state["selected_name"]
    row = df[df["full_name"] == selected_name].iloc[0]
    # re-sync name list index
    current_index = names.index(selected_name)


# -------------------------------
# Main Header
# -------------------------------
st.markdown(f"<h2 style='margin-top:20px;'>{row['full_name']}</h2>", unsafe_allow_html=True)


# -------------------------------
# 3-Column Compact Layout
# -------------------------------
colA, colB, colC = st.columns(3)

# ---- Work Experience ----
with colA:
    st.markdown("### 🧑‍⚕️ Work Experience")
    if row["work_experience"]:
        for exp in row["work_experience"]:
            st.markdown(f"**{exp.get('employer','N/A')} — {exp.get('role','N/A')}**")
            st.markdown(f"{exp.get('start','N/A')} → {exp.get('end','N/A')}")
            st.markdown(f"{exp.get('location','N/A')}")
            # sources
            if "source" in exp and exp["source"]:
                st.markdown(
                    "<ul>" + "".join([f"<li><a href='{s}' target='_blank'>{s}</a></li>" for s in exp["source"]]) + "</ul>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
    else:
        st.markdown("N/A")

# ---- Residency ----
with colB:
    st.markdown("### 🏥 Residency")
    if row["residency"]:
        for res in row["residency"]:
            st.markdown(f"**{res.get('institution','N/A')}**")
            st.markdown(f"{res.get('start_year','N/A')} → {res.get('end_year','N/A')}")
            if "source" in res and res["source"]:
                st.markdown(
                    "<ul>" + "".join([f"<li><a href='{s}' target='_blank'>{s}</a></li>" for s in res["source"]]) + "</ul>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
    else:
        st.markdown("N/A")

# ---- Medical School ----
with colC:
    st.markdown("### 🎓 Medical School")
    if row["medical_school"]:
        for edu in row["medical_school"]:
            st.markdown(f"**{edu.get('institution','N/A')}**")
            st.markdown(f"{edu.get('start_year','N/A')} → {edu.get('end_year','N/A')}")
            if "source" in edu and edu["source"]:
                st.markdown(
                    "<ul>" + "".join([f"<li><a href='{s}' target='_blank'>{s}</a></li>" for s in edu["source"]]) + "</ul>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
    else:
        st.markdown("N/A")


# -------------------------------
# Secondary Horizontal Row
# -------------------------------
st.markdown("---")
st.markdown("### Additional Details")

detA, detB, detC, detD, detE = st.columns(5)

# NPI
with detA:
    st.markdown("**NPI**")
    npi = safe_str(row["NPI"])
    st.markdown(
        f"<a href='https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi}' target='_blank'>{npi}</a>",
        unsafe_allow_html=True,
    )

# Doximity
with detB:
    st.markdown("**Doximity**")
    link = safe_str(row["doximity_url"])
    if link and link.lower() != "nan":
        st.markdown(f"<a href='{link}' target='_blank'>{link}</a>", unsafe_allow_html=True)
    else:
        st.markdown("N/A")

# LinkedIn
with detC:
    st.markdown("**LinkedIn**")
    link = safe_str(row["linkedin_url"])
    if link and link.lower() != "nan":
        st.markdown(f"<a href='{link}' target='_blank'>{link}</a>", unsafe_allow_html=True)
    else:
        st.markdown("N/A")

# Emails
with detD:
    st.markdown("**Emails**")
    if row["emails"]:
        for e in row["emails"]:
            st.markdown(f"- {e}")
    else:
        st.markdown("N/A")

# Insurance
with detE:
    st.markdown("**Insurance**")
    if row["insurance_accepted"]:
        for ins in row["insurance_accepted"]:
            st.markdown(f"- {ins}")
    else:
        st.markdown("N/A")
