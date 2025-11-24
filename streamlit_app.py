import streamlit as st
import pandas as pd
import ast

# ----------------------------------------------------------
#                     PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Physician Profile Viewer",
    layout="wide",
)

st.markdown(
    """
    <style>
        body { background-color: #fafafa !important; }
        .block-container { padding-top: 2rem; }
        .stSelectbox { max-width: 450px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
#                     SMART CSV LOADER
# ----------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # --- Helper to safely parse dict/list fields ---
    def parse(x):
        if pd.isna(x) or x == "" or x == "N/A":
            return None
        try:
            return ast.literal_eval(x)
        except:
            return x

    # All possible column aliases → normalized names
    col_map = {
        # NAME
        "full_name": "full_name",
        "cleaned.full_name": "full_name",
        "raw_name": "full_name",
        "name": "full_name",

        # NPI
        "npi": "npi",
        "NPI": "npi",
        "raw_npi": "npi",

        # Work Experience
        "work_experience": "work_experience",
        "work_experience_json": "work_experience",
        "raw_work_experience": "work_experience",

        # Residency
        "residency": "residency",
        "residency_json": "residency",

        # Medical School
        "medical_school": "medical_school",
        "raw_medical_school": "medical_school",

        # Emails
        "emails": "emails",
        "emails_json": "emails",
        "raw_emails": "emails",

        # Insurance
        "insurance": "insurance",
        "raw_insurance": "insurance",

        # URLs
        "doximity_url": "doximity_url",
        "raw_doximity_url": "doximity_url",
        "linkedin_url": "linkedin_url",
        "raw_linkedin_url": "linkedin_url",
    }

    # Normalize discovered columns
    normalized = {}
    for col in df.columns:
        key = col_map.get(col)
        if key:
            normalized[key] = df[col]

    # Build final clean DataFrame
    final = pd.DataFrame()

    # --- Mandatory field ---
    final["full_name"] = (
        normalized.get("full_name", df[df.columns[0]])
        .fillna("Unknown")
        .astype(str)
    )

    # --- Simple fields ---
    final["npi"] = normalized.get("npi", None)
    final["doximity_url"] = normalized.get("doximity_url", None)
    final["linkedin_url"] = normalized.get("linkedin_url", None)

    # --- Parsed JSON-like fields ---
    for key in ["work_experience", "residency", "medical_school", "emails", "insurance"]:
        if key in normalized:
            final[key] = normalized[key].apply(parse)
        else:
            final[key] = None

    return final


df = load_data()

# ==========================================================
#                     UI RENDERING HELPERS
# ==========================================================

def render_section(header, items):
    """Renders a list of dicts like work experience."""
    st.subheader(header)

    if items is None or items == "" or items == []:
        st.markdown("**N/A**")
        return

    if isinstance(items, dict):
        items = [items]

    for item in items:
        if not isinstance(item, dict):
            st.markdown(f"- {item}")
            continue

        # Pretty key-value display
        bullets = []
        for k, v in item.items():
            if k == "source" and isinstance(v, list):
                # clickable links
                links = "<br>".join([f"<a href='{x}' target='_blank'>{x}</a>" for x in v])
                bullets.append(f"**Sources:**<br>{links}")
            else:
                bullets.append(f"**{k.capitalize()}:** {v}")

        st.markdown("<br>".join(bullets), unsafe_allow_html=True)
        st.markdown("---")


def render_details(row):
    st.subheader("Details")

    npi_val = row["npi"] if pd.notna(row["npi"]) else "N/A"
    dox = row.get("doximity_url", "N/A")
    lin = row.get("linkedin_url", "N/A")

    # Make NPI clickable
    if npi_val != "N/A":
        npi_link = f"[{npi_val}](https://npiregistry.cms.hhs.gov/registry/search-results-table?number={npi_val})"
    else:
        npi_link = "N/A"

    st.markdown(f"**NPI:** {npi_link}")
    st.markdown(f"**Emails:** {row['emails'] if row['emails'] else 'N/A'}")
    st.markdown(f"**Insurance:** {row['insurance'] if row['insurance'] else 'N/A'}")

    if dox and str(dox) != "nan":
        st.markdown(f"**Doximity:** <a href='{dox}' target='_blank'>{dox}</a>", unsafe_allow_html=True)
    else:
        st.markdown("**Doximity:** N/A")

    if lin and str(lin) != "nan":
        st.markdown(f"**LinkedIn:** <a href='{lin}' target='_blank'>{lin}</a>", unsafe_allow_html=True)
    else:
        st.markdown("**LinkedIn:** N/A")


# ==========================================================
#                     PAGE UI
# ==========================================================

st.title("📘 Physician Profile Viewer")
st.write("Select a physician to view enrichment results.")

physicians = sorted(df["full_name"].unique().tolist())
selected_name = st.selectbox("Choose Physician:", physicians)

row = df[df["full_name"] == selected_name].iloc[0]

st.header(selected_name)

col1, col2, col3 = st.columns(3)

with col1:
    render_section("💼 Work Experience", row["work_experience"])

with col2:
    render_section("🧑‍⚕️ Residency", row["residency"])

with col3:
    render_section("🎓 Medical School", row["medical_school"])

st.markdown("---")
render_details(row)
