import streamlit as st
import pandas as pd
import ast

# -------------------------
# Load CSV
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Safe parser for list/dict fields
    def parse(x):
        if pd.isna(x) or x == "":
            return None
        try:
            return ast.literal_eval(x)
        except:
            return x

    list_fields = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted",
    ]

    for col in list_fields:
        if col in df.columns:
            df[col] = df[col].apply(parse)
        else:
            df[col] = None

    return df


df = load_data()

st.set_page_config(page_title="Physician Viewer", layout="wide")

st.title("📘 Physician Profile Viewer")
st.write("Select a physician to view enrichment results.")

# --------------------------------
# Left column: dropdown
# --------------------------------
left, right = st.columns([1, 3])

with left:
    all_names = sorted(df["raw.name"].fillna("Unknown").tolist())
    selected_name = st.selectbox("Choose Physician:", all_names, index=0)

row = df[df["raw.name"] == selected_name].iloc[0]

# --------------------------------
# Utility renderers
# --------------------------------
def render_list(label, data):
    st.subheader(label)
    if data is None or data == []:
        st.write("N/A")
    else:
        for item in data:
            st.write(f"- {item}")

# --------------------------------
# Main Layout
# --------------------------------
with right:
    st.header(selected_name)

    col1, col2, col3 = st.columns(3)

    # Work Experience
    with col1:
        render_list("Work Experience", row["cleaned.work_experience"])

    # Residency
    with col2:
        render_list("Residency", row["cleaned.residency"])

    # Medical School
    with col3:
        render_list("Medical School", row["cleaned.medical_school"])

    st.markdown("---")

    # -------------------------
    # Extra Information
    # -------------------------
    st.subheader("Details")

    st.write(f"**NPI:** {row['npi']}")
    
    # Email list
    emails = row["cleaned.emails"]
    st.write("**Emails:**")
    if emails:
        for e in emails:
            st.write(f"- {e}")
    else:
        st.write("N/A")

    ins = row["cleaned.insurance_accepted"]
    st.write("**Insurance:**")
    if ins:
        for i in ins:
            st.write(f"- {i}")
    else:
        st.write("N/A")

    # Links
    st.write("**Doximity:**")
    dox = row["cleaned.doximity_url.url"]
    st.write(dox if isinstance(dox, str) and dox.startswith("http") else "N/A")

    st.write("**LinkedIn:**")
    li = row["cleaned.linkedin_url.url"]
    st.write(li if isinstance(li, str) and li.startswith("http") else "N/A")
