import streamlit as st
import pandas as pd
import ast

# -------------------------------
# UI CONFIG
# -------------------------------
st.set_page_config(
    page_title="Physician Profile Viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    body { background-color: #fafafa !important; }
    .block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD CSV
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Columns containing list/dict-like strings
    json_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.insurance_accepted",
        "cleaned.emails"
    ]

    def try_parse(x):
        if pd.isna(x) or x == "" or x in ["[]", "{}", "None"]:
            return []
        try:
            return ast.literal_eval(x)
        except:
            return []

    for c in json_cols:
        if c in df.columns:
            df[c] = df[c].apply(try_parse)

    return df

df = load_data()

# -------------------------------
# MAIN HEADER
# -------------------------------
st.title("📘 Physician Profile Viewer")

# -------------------------------
# DROPDOWN
# -------------------------------
if "cleaned.name" not in df.columns:
    st.error("CSV missing `cleaned.name` column.")
    st.stop()

physicians = sorted(df["cleaned.name"].tolist())

selected_name = st.selectbox(
    "Choose Physician:",
    physicians,
    index=0
)

row = df[df["cleaned.name"] == selected_name].iloc[0]

# -------------------------------
# HELPER: display list of dicts
# -------------------------------
def render_section(list_of_dicts):
    if not list_of_dicts:
        st.write("N/A")
        return

    for item in list_of_dicts:
        line = ""
        for key, val in item.items():
            if key == "source":
                continue  # don't display confidence/source junk
            if isinstance(val, str) and val.strip() == "":
                continue
            line += f"**{key.replace('_',' ').title()}**: {val} — "
        if line.endswith(" — "):
            line = line[:-3]
        st.markdown(f"- {line}")

        # Sources as links
        if "source" in item:
            for src in item["source"]:
                st.markdown(f"  • [{src}]({src})")

# -------------------------------
# MAIN DISPLAY
# -------------------------------
st.markdown(f"## {row['cleaned.name']}")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💼 Work Experience")
    render_section(row["cleaned.work_experience"])

with col2:
    st.markdown("### 🧑‍⚕️ Residency")
    render_section(row["cleaned.residency"])

with col3:
    st.markdown("### 🎓 Medical School")
    render_section(row["cleaned.medical_school"])

st.markdown("---")
st.markdown("## Details")

colA, colB, colC, colD, colE = st.columns(5)

# NPI
with colA:
    st.markdown("**NPI**")
    npi = str(row["cleaned.npi"])
    st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/provider-view/{npi})")

# Doximity
with colB:
    st.markdown("**Doximity**")
    dox = row["cleaned.doximity_url.url"] if "cleaned.doximity_url.url" in row else "N/A"
    st.markdown(dox if dox == "N/A" else f"[{dox}]({dox})")

# LinkedIn
with colC:
    st.markdown("**LinkedIn**")
    li = row["cleaned.linkedin_url.url"] if "cleaned.linkedin_url.url" in row else "N/A"
    st.markdown(li if li == "N/A" else f"[{li}]({li})")

# Emails
with colD:
    st.markdown("**Emails**")
    emails = row["cleaned.emails"]
    if not emails:
        st.write("N/A")
    else:
        for e in emails:
            st.markdown(f"- {e.get('email','N/A')}")

# Insurance
with colE:
    st.markdown("**Insurance**")
    ins = row["cleaned.insurance_accepted"]
    if not ins:
        st.write("N/A")
    else:
        for i in ins:
            st.markdown(f"- {i.get('insurance','N/A')}")
            for src in i.get("source", []):
                st.markdown(f"  • [{src}]({src})")
