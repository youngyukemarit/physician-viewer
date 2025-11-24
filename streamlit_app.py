import streamlit as st
import pandas as pd

# --------------------------------------------------------
# LOAD CLEAN CSV
# --------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Guarantee consistent types
    list_cols = ["work_experience", "residency", "medical_school", "emails", "insurance"]
    for col in list_cols:
        df[col] = df[col].apply(lambda x: [] if pd.isna(x) or x == "" else eval(x))

    # String fields
    df["doximity"] = df["doximity"].fillna("")
    df["linkedin"] = df["linkedin"].fillna("")
    
    return df

df = load_data()

# Sorted alphabetical physician names
physicians = sorted(df["full_name"].unique())

# --------------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------------
st.sidebar.title("Select Physician")
selected_name = st.sidebar.selectbox("Choose a physician:", physicians)

row = df[df["full_name"] == selected_name].iloc[0]

# --------------------------------------------------------
# TITLE
# --------------------------------------------------------
st.title(selected_name)

# --------------------------------------------------------
# 3-COLUMN TOP SECTION
# --------------------------------------------------------
col1, col2, col3 = st.columns(3)

# -------- WORK EXPERIENCE --------
with col1:
    st.subheader("🧑‍⚕️ Work Experience")
    if len(row.work_experience) == 0:
        st.write("N/A")
    else:
        for w in row.work_experience:
            st.markdown(f"**{w.get('employer','N/A')} — {w.get('role','N/A')}**")
            st.write(f"{w.get('start','N/A')} → {w.get('end','N/A')}")
            st.write(w.get("location","N/A"))
            for link in w.get("source", []):
                st.markdown(f"- [{link}]({link})")

# -------- RESIDENCY --------
with col2:
    st.subheader("👨‍⚕️ Residency")
    if len(row.residency) == 0:
        st.write("N/A")
    else:
        for r in row.residency:
            st.markdown(f"**{r.get('institution','N/A')}**")
            st.write(f"{r.get('start_year','N/A')} → {r.get('end_year','N/A')}")
            for link in r.get("source", []):
                st.markdown(f"- [{link}]({link})")

# -------- MED SCHOOL --------
with col3:
    st.subheader("🎓 Medical School")
    if len(row.medical_school) == 0:
        st.write("N/A")
    else:
        for m in row.medical_school:
            st.markdown(f"**{m.get('institution','N/A')}**")
            st.write(f"{m.get('start_year','N/A')} → {m.get('end_year','N/A')}")
            for link in m.get("source", []):
                st.markdown(f"- [{link}]({link})")

# --------------------------------------------------------
# ADDITIONAL DETAILS (BOTTOM SECTION)
# --------------------------------------------------------
st.markdown("---")
st.subheader("Additional Details")
ad1, ad2, ad3, ad4 = st.columns(4)

# NPI
with ad1:
    st.write("**NPI**")
    npi = str(row["npi"])
    if npi != "nan":
        st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi})")
    else:
        st.write("N/A")

# Doximity
with ad2:
    st.write("**Doximity**")
    if row["doximity"]:
        st.markdown(f"[{row['doximity']}]({row['doximity']})")
    else:
        st.write("N/A")

# LinkedIn
with ad3:
    st.write("**LinkedIn**")
    if row["linkedin"]:
        st.markdown(f"[{row['linkedin']}]({row['linkedin']})")
    else:
        st.write("N/A")

# Emails & Insurance
with ad4:
    st.write("**Emails & Insurance**")

    # Emails
    st.write("**Emails:**")
    if len(row.emails) == 0:
        st.write("N/A")
    else:
        for e in row.emails:
            st.write(f"- {e.get('email')} ({e.get('type')})")

    # Insurance
    st.write("**Insurance:**")
    if len(row.insurance) == 0:
        st.write("N/A")
    else:
        for i in row.insurance:
            st.write(f"- {i.get('insurance')}")

