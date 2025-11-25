import streamlit as st
import pandas as pd
import ast

# =========================
# SAFE PARSING HELPERS
# =========================

def safe_parse(x):
    if pd.isna(x) or x in ["", "nan", None]:
        return []
    try:
        return ast.literal_eval(str(x))
    except:
        return []

def pick_value(row, keys, default="N/A"):
    for c in keys:
        if c in row and not pd.isna(row[c]):
            val = str(row[c]).strip()
            if val not in ["", "nan", "None"]:
                return val
    return default


# =========================
# LOAD DATA (SAFE)
# =========================

@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    list_cols = [
        "cleaned.work_experience", "cleaned.residency",
        "cleaned.medical_school", "cleaned.insurance_accepted",
        "cleaned.emails"
    ]

    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    return df


df = load_data()

# Build physician list: "NAME — NPI"
df["display"] = df["cleaned.name"] + " — " + df["cleaned.npi"].astype(str)
physician_list = df["display"].tolist()


# =========================
# SESSION STATE INDEX
# =========================

if "index" not in st.session_state:
    st.session_state.index = 0


# =========================
# CSS — LIGHT MODE + FONTS + DROPDOWN WIDTH
# =========================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #222 !important;
    font-family: 'Inter', sans-serif !important;
}

/* dropdown width */
.dropdown-container {
    width: 33% !important;
}

/* remove dark background on selectbox */
.stSelectbox > div > div {
    background-color: #ffffff !important;
    color: #222 !important;
    border: 1px solid #ccc !important;
}

</style>
""", unsafe_allow_html=True)


# =========================
# PAGE HEADER
# =========================

st.title("📘 Physician Profile Viewer")


# =========================
# TOP BAR: DROPDOWN + NAV BUTTONS
# =========================

colA, colB, colC = st.columns([2, 0.25, 0.25])

with colA:
    st.markdown('<div class="dropdown-container">', unsafe_allow_html=True)
    selected = st.selectbox("Choose Physician:", physician_list,
                            index=st.session_state.index)
    st.markdown('</div>', unsafe_allow_html=True)

# compute current index
current_index = physician_list.index(selected)


with colB:
    if st.button("← Prev", use_container_width=True):
        st.session_state.index = max(current_index - 1, 0)
        st.experimental_rerun()

with colC:
    if st.button("Next →", use_container_width=True):
        st.session_state.index = min(current_index + 1, len(physician_list)-1)
        st.experimental_rerun()


# =========================
# SELECTED RECORD
# =========================

row = df.iloc[current_index]

name = row["cleaned.name"]
npi = str(row["cleaned.npi"])

st.header(name)


# =========================
# FORMAT WORK EXPERIENCE BLOCKS
# =========================

def render_experience_block(items):
    if not items:
        st.write("N/A")
        return

    for exp in items:
        employer = exp.get("employer", "N/A")
        role = exp.get("role", "N/A")
        start = exp.get("start", "N/A")
        end = exp.get("end", "N/A")
        location = exp.get("location", "N/A")
        srcs = exp.get("source", [])

        st.markdown(f"""
        **Employer:** {employer}  
        **Role:** {role}  
        **Start:** {start}  
        **End:** {end}  
        **Location:** {location}
        """)

        for s in srcs:
            st.markdown(f"- [{s}]({s})")

        st.write("---")


# =========================
# 3 COLUMN SECTIONS
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧳 Work Experience")
    render_experience_block(row["cleaned.work_experience"])

with col2:
    st.subheader("👨‍⚕️ Residency")
    render_experience_block(row["cleaned.residency"])

with col3:
    st.subheader("🎓 Medical School")
    render_experience_block(row["cleaned.medical_school"])


# =========================
# DETAILS SECTION
# =========================

st.subheader("Details")

# NPI → FIXED URL (correct provider-view page)
npi_url = f"https://npiregistry.cms.hhs.gov/provider-view/{npi}"
st.markdown(f"**NPI:** [{npi}]({npi_url})")

# LinkedIn fix (no hyperlink for nan)
linkedin = pick_value(row, ["cleaned.linkedin_url.url", "raw.linkedin_url.url"])
if linkedin.lower() in ["nan", "n/a", "none", ""]:
    linkedin_display = "N/A"
else:
    linkedin_display = f"[{linkedin}]({linkedin})"

st.markdown(f"**LinkedIn:** {linkedin_display}")

# Doximity
dox = pick_value(row, ["cleaned.doximity_url.url"])
if dox not in ["N/A", "nan", "None", ""]:
    st.markdown(f"**Doximity:** [{dox}]({dox})")
else:
    st.markdown("**Doximity:** N/A")

# Emails
emails = row["cleaned.emails"]
if not emails:
    st.markdown("**Emails:** N/A")
else:
    for e in emails:
        st.markdown(f"- {e}")

# Insurance
insurance = row["cleaned.insurance_accepted"]
if not insurance:
    st.markdown("**Insurance:** N/A")
else:
    st.markdown("**Insurance:**")
    for ins in insurance:
        ins_name = ins.get("insurance", "N/A")
        ins_srcs = ins.get("source", [])
        st.write(f"- {ins_name}")
        for s in ins_srcs:
            st.markdown(f"  • [{s}]({s})")
