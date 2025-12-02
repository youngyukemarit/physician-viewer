import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer", layout="wide")

# ---- Light theme override ----
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAFA !important;
        color: #222222 !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border-radius: 6px !important;
        border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="select"] span {
        color: #222222 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    # Load the newly created, clean file which now includes citations
    df = pd.read_csv("v7_viewer/viewer_data.csv")

    # List of columns that contain string representations of Python lists/dictionaries
    list_columns = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.citations" # INCLUDE THE NEW CITATIONS COLUMN
    ]

    for col in list_columns:
        # The data is a string representation of a list of dicts: '[{"employer": ...}]'
        # ast.literal_eval safely converts this string back to a Python object.
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])

    return df

# Load the data immediately
df = load_data()

# -------------------------
# Font
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-weight:700;'>📘 Physician Profile Viewer</h1>", unsafe_allow_html=True)

# -------------------------
# Dropdown + Next/Prev Navigation (Robust Initialization)
# -------------------------
physicians = sorted(df["cleaned.name"].fillna("Unknown").unique().tolist())

# Robust Initialization to prevent the AttributeError on initial load
if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

if "selected_name" not in st.session_state or st.session_state.selected_name not in physicians:
    st.session_state.selected_name = physicians[st.session_state.selected_index]


def choose_physician():
    # When the user changes the box, we update the index based on the new name
    st.session_state.selected_index = physicians.index(st.session_state.selected_name)


# Row layout: dropdown on left, arrows far right
col_dd, col_spacer, col_prev, col_next = st.columns([0.33, 0.47, 0.10, 0.10])

with col_dd:
    st.selectbox(
        "Choose Physician:",
        physicians,
        key="selected_name",
        index=st.session_state.selected_index,
        on_change=choose_physician
    )

# Light-mode button styling
light_btn_css = """
<style>
div.stButton > button {
    background-color: #FFFFFF !important;
    color: #222222 !important;
    border: 1px solid #CCCCCC !important;
    border-radius: 6px !important;
}
div.stButton > button:hover {
    background-color: #F0F0F0 !important;
}
</style>
"""
st.markdown(light_btn_css, unsafe_allow_html=True)

# Navigation buttons now update the index which automatically updates the selectbox
with col_prev:
    if st.button("⬅️ Prev", use_container_width=True):
        st.session_state.selected_index = max(0, st.session_state.selected_index - 1)
        st.session_state.selected_name = physicians[st.session_state.selected_index]

with col_next:
    if st.button("Next ➡️", use_container_width=True):
        st.session_state.selected_index = min(len(physicians) - 1, st.session_state.selected_index + 1)
        st.session_state.selected_name = physicians[st.session_state.selected_index]


selected_name = physicians[st.session_state.selected_index]


# -------------------------
# Select row
# -------------------------
row = df[df["cleaned.name"] == selected_name].iloc[0]

# -------------------------
# Section renderer
# -------------------------
def show_section(title, items):
    st.markdown(f"<h3 style='margin-top:20px;'>{title}</h3>", unsafe_allow_html=True)
    if not items:
        st.write("N/A")
        return
    for entry in items:
        lines = []
        # Use keys that are present in the enriched data
        for key in ["employer", "institution", "role", "start", "start_year", "end", "end_year", "location"]:
            if key in entry and entry[key] not in ["N/A", None, ""]:
                pretty = key.replace("_", " ").title()
                lines.append(f"**{pretty}:** {entry[key]}")
        if lines:
            st.markdown("<br>".join(lines), unsafe_allow_html=True)
        if "source" in entry and entry["source"]:
            st.write("- " + entry["source"][0])

# -------------------------
# Name
# -------------------------
st.markdown(f"<h2 style='margin-top:10px;'>{row['cleaned.name']}</h2>", unsafe_allow_html=True)

# -------------------------
# Columns for Experience / Residency / Medical School
# -------------------------
col1, col2, col3 = st.columns(3)

with col1:
    show_section("👔 Work Experience", row["cleaned.work_experience"])

with col2:
    show_section("👨‍⚕️ Residency", row["cleaned.residency"])

with col3:
    show_section("🎓 Medical School", row["cleaned.medical_school"])

# -------------------------
# Details Section
# -------------------------
st.markdown("<h2 style='margin-top:35px;'>Details</h2>", unsafe_allow_html=True)

colA, colB, colC, colD = st.columns(4)

with colA:
    st.markdown("**NPI:**")
    npi = str(row["cleaned.npi"])
    st.markdown(f"[{npi}](https://npiregistry.cms.hhs.gov/provider-view/{npi})")

with colB:
    st.markdown("**Doximity:**")
    dox = row.get("cleaned.doximity_url.url", "N/A")
    if isinstance(dox, str) and dox.startswith("http"):
        st.markdown(f"[{dox}]({dox})")
    else:
        st.write("N/A")

with colC:
    st.markdown("**LinkedIn:**")
    linkedin = row.get("cleaned.linkedin_url.url", "N/A")
    if isinstance(linkedin, str) and linkedin.startswith("http"):
        st.markdown(f"[{linkedin}]({linkedin})")
    else:
        st.write("N/A")

with colD:
    st.markdown("**License State:**")
    st.write(row["license_state"])

# -------------------------
# Citations Section (NEW SECTION FOR LINKS)
# -------------------------
st.markdown("<h2 style='margin-top:35px;'>🔗 Source Citations</h2>", unsafe_allow_html=True)

citations = row["cleaned.citations"]

if citations:
    for i, url in enumerate(citations):
        st.markdown(f"**Source {i+1}:** [{url}]({url})")
else:
    st.write("No direct citations were provided by the enrichment model for this profile.")
