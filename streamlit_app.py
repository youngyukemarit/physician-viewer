import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def safe_parse(x):
    if pd.isna(x) or x == "" or str(x).strip() == "N/A":
        return None
    try:
        return ast.literal_eval(x)
    except:
        return x

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Parse cleaned JSON columns
    json_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted"
    ]

    for col in json_cols:
        df[col] = df[col].apply(safe_parse)

    return df

df = load_data()

# -----------------------------
# UI
# -----------------------------
st.title("📘 Physician Profile Viewer")
st.write("Select a physician to view enrichment results.")

# Use raw.name as the selection key
names = sorted(df["raw.name"].fillna("Unknown").tolist())

selected_name = st.selectbox("Choose Physician:", names)

row = df[df["raw.name"] == selected_name].iloc[0]

st.header(selected_name)

# -----------------------------
# Layout: 3-column structure
# -----------------------------
col1, col2, col3 = st.columns(3)

# ========== Work Experience ==========
with col1:
    st.subheader("💼 Work Experience")
    exp = row["cleaned.work_experience"]
    if not exp:
        st.write("N/A")
    else:
        for item in exp:
            st.markdown(f"**{item.get('employer','N/A')} — {item.get('role','N/A')}**")
            st.write(f"{item.get('start','N/A')} → {item.get('end','N/A')}")
            st.write(item.get("location", "N/A"))
            if "source" in item:
                for url in item["source"]:
                    st.markdown(f"- [{url}]({url})")
            st.markdown("---")

# ========== Residency ==========
with col2:
    st.subheader("🧑‍⚕️ Residency")
    res = row["cleaned.residency"]
    if not res:
        st.write("N/A")
    else:
        for item in res:
            st.markdown(f"**{item.get('institution','N/A')}**")
            st.write(f"{item.get('start_year','N/A')} → {item.get('end_year','N/A')}")
            if "source" in item:
                for url in item["source"]:
                    st.markdown(f"- [{url}]({url})")
            st.markdown("---")

# ========== Medical School ==========
with col3:
    st.subheader("🎓 Medical School")
    med = row["cleaned.medical_school"]
    if not med:
        st.write("N/A")
    else:
        for item in med:
            st.markdown(f"**{item.get('institution','N/A')}**")
            st.write(f"{item.get('start_year','N/A')} → {item.get('end_year','N/A')}")
            if "source" in item:
                for url in item["source"]:
                    st.markdown(f"- [{url}]({url})")
            st.markdown("---")

# -----------------------------
# Additional Details
# -----------------------------
st.subheader("Details")

npi = row["npi"]
st.write(f"**NPI:** [{npi}](https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi})")

# Emails
emails = row["cleaned.emails"]
st.write("**Emails:**")
if not emails:
    st.write("N/A")
else:
    for e in emails:
        st.write(f"- {e.get('email','N/A')} ({e.get('type','N/A')})")

# Insurance
ins = row["cleaned.insurance_accepted"]
st.write("**Insurance:**")
if not ins:
    st.write("N/A")
else:
    for i in ins:
        st.write(f"- {i.get('insurance','N/A')}")

# Doximity
dox = row.get("cleaned.doximity_url.url", None)
st.write("**Doximity:**")
st.write(dox if dox else "N/A")

# LinkedIn
li = row.get("cleaned.linkedin_url.url", None)
st.write("**LinkedIn:**")
st.write(li if li else "N/A")
