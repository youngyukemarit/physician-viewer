import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Physician Viewer", layout="wide", initial_sidebar_state="expanded")

# Load dataset safely
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")
    df = df.sort_values("full_name").reset_index(drop=True)
    return df

df = load_data()

# -------------------------
# JSON PARSING HELPERS
# -------------------------
def parse_json(val):
    """Return a list or dict, never NaN or empty string."""
    if pd.isna(val) or val in ("", "[]", "{}"):
        return []
    try:
        obj = json.loads(val)
        return obj if isinstance(obj, (list, dict)) else []
    except:
        return []

# -------------------------
# SIDEBAR — PHYSICIAN SELECTOR
# -------------------------
st.sidebar.title("Select Physician")

physicians = df["full_name"].tolist()

selected = st.sidebar.selectbox(
    "Choose a physician:",
    physicians,
    index=0,
)

idx = physicians.index(selected)

# Navigation buttons
col_prev, col_next = st.sidebar.columns(2)

if col_prev.button("⬅ Prev"):
    idx = max(0, idx - 1)
if col_next.button("Next ➡"):
    idx = min(len(df) - 1, idx + 1)

row = df.iloc[idx]

# -------------------------
# MAIN PROFILE HEADER
# -------------------------
st.title(row.full_name)

# NEXT/PREV TOP RIGHT
top_left, top_spacer, top_right = st.columns([10, 1, 2])
with top_right:
    if st.button("Next ➡ (Top)"):
        idx = min(len(df)-1, idx+1)

# -------------------------
# THREE-COLUMN LAYOUT
# -------------------------
work_col, res_col, med_col = st.columns(3)

# ---- WORK EXPERIENCE ----
with work_col:
    st.subheader("💼 Work Experience")
    we = parse_json(row.get("work_experience_json", ""))
    if not we:
        st.write("N/A")
    else:
        for item in we:
            st.markdown(f"**{item.get('employer','N/A')} — {item.get('role','N/A')}**")
            st.write(f"{item.get('start','N/A')} → {item.get('end','N/A')}")
            st.write(item.get("location","N/A"))
            for src in item.get("source", []):
                st.markdown(f"- [{src}]({src})")
            st.markdown("---")

# ---- RESIDENCY ----
with res_col:
    st.subheader("🧑‍⚕️ Residency")
    rs = parse_json(row.get("residency_json", ""))
    if not rs:
        st.write("N/A")
    else:
        for item in rs:
            st.markdown(f"**{item.get('institution','N/A')}**")
            st.write(f"{item.get('start_year','N/A')} → {item.get('end_year','N/A')}")
            for src in item.get("source", []):
                st.markdown(f"- [{src}]({src})")
            st.markdown("---")

# ---- MEDICAL SCHOOL ----
with med_col:
    st.subheader("🎓 Medical School")
    ms = parse_json(row.get("medical_school_json", ""))
    if not ms:
        st.write("N/A")
    else:
        for item in ms:
            st.markdown(f"**{item.get('name','N/A')}**")
            st.write(f"{item.get('year','N/A')}")
            for src in item.get("source", []):
                st.markdown(f"- [{src}]({src})")
            st.markdown("---")

# -------------------------
# ADDITIONAL DETAILS UNDERNEATH
# -------------------------
st.markdown("---")
st.subheader("Additional Details")

det1, det2, det3, det4 = st.columns(4)

with det1:
    st.write("**NPI**")
    npi = row.get("NPI", "")
    st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi})")

with det2:
    st.write("**Doximity**")
    dox = row.get("doximity", "N/A")
    if pd.isna(dox) or not str(dox).startswith("http"):
        st.write("N/A")
    else:
        st.markdown(f"[{dox}]({dox})")

with det3:
    st.write("**LinkedIn**")
    li = row.get("linkedin", "N/A")
    if pd.isna(li) or not str(li).startswith("http"):
        st.write("N/A")
    else:
        st.markdown(f"[{li}]({li})")

with det4:
    st.write("**Emails & Insurance**")
    emails = parse_json(row.get("emails_json", ""))
    ins = parse_json(row.get("insurance_json", ""))
    
    if not emails:
        st.write("Emails: N/A")
    else:
        st.write("Emails:")
        for e in emails:
            st.write(f"- {e.get('email')} ({e.get('type','')})")

    if not ins:
        st.write("Insurance: N/A")
    else:
        st.write("Insurance:")
        for i in ins:
            st.write(f"- {i.get('insurance','N/A')}")
