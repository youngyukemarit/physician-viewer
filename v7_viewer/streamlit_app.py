import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Physician Profile Viewer (V7) - Gemini", layout="wide")

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
    # Corrected file path for Streamlit Cloud deployment
    df = pd.read_csv("v7_viewer/viewer_data.csv")

    # List of columns that contain string representations of Python lists/dictionaries
    # We remove 'cleaned.citations' as those sources are now nested within other columns
    list_columns = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school"
    ]

    for col in list_columns:
        # ast.literal_eval safely converts the string literal back to a Python object.
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])

    return df

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
# Dropdown + Next/Prev Navigation (FINAL STABLE VERSION)
# -------------------------
physicians = sorted(df["cleaned.name"].fillna("Unknown").unique().tolist())

# Robust Initialization
if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

# Callback function to update the index when the user selects a name from the dropdown
def update_index_from_selectbox():
    # st.session_state.selectbox_name is the value chosen by the user
    name = st.session_state.selectbox_name
    st.session_state.selected_index = physicians.index(name)

# Get the name corresponding to the current index for the initial display value
current_name = physicians[st.session_state.selected_index]
current_index = st.session_state.selected_index

# Row layout: dropdown on left, arrows far right
col_dd, col_spacer, col_prev, col_next = st.columns([0.33, 0.47, 0.10, 0.10])

with col_dd:
    # The selectbox uses a key and an on_change handler to update the index state
    st.selectbox(
        "Choose Physician:",
        physicians,
        index=current_index,
        key="selectbox_name",
        on_change=update_index_from_selectbox
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


# Navigation buttons: Manually update the index ONLY.
with col_prev:
    if st.button("⬅️ Prev", use_container_width=True):
        st.session_state.selected_index = max(0, current_index - 1)

with col_next:
    if st.button("Next ➡️", use_container_width=True):
        st.session_state.selected_index = min(len(physicians) - 1, current_index + 1)


# The final selected name is always derived from the final state of the index
selected_name = physicians[st.session_state.selected_index]

# -------------------------
# Select row
# -------------------------
row = df[df["cleaned.name"] == selected_name].iloc[0]

# -------------------------
# Section renderer (UPDATED FOR INLINE CITATIONS)
# -------------------------
def show_section(title, items):
    st.markdown(f"<h3 style='margin-top:20px;'>{title}</h3>", unsafe_allow_html=True)
    if not items:
        st.write("N/A")
        return
    for entry in items:
        lines = []
        source_url = None
        
        # 1. Collect all the standard detail lines
        # Also look for the 'source' key to extract the URL
        for key in ["employer", "institution", "role", "start", "start_year", "end", "end_year", "location", "source"]:
            if key in entry and entry[key] not in ["N/A", None, ""]:
                if key == "source":
                    # Capture the source URL separately
                    source_url = entry[key]
                else:
                    # Display standard details
                    pretty = key.replace("_", " ").title()
                    lines.append(f"**{pretty}:** {entry[key]}")
        
        # 2. Add the source URL as the last line for this entry
        if source_url:
            source_link = None
            if isinstance(source_url, list) and source_url:
                # Handle source as a list (use the first one)
                source_link = source_url[0]
            elif isinstance(source_url, str) and source_url.startswith("http"):
                # Handle source as a single URL string
                source_link = source_url
                
            if source_link:
                lines.append(f"**Source:** <a href='{source_link}' target='_blank' style='text-decoration: none;'>{source_link}</a>")

        if lines:
            st.markdown("<br>".join(lines), unsafe_allow_html=True)

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
# Removed Citations Section
# -------------------------
# The source citations are now integrated into the work experience, residency, and medical school sections.
