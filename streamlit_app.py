import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Physician Profiles")

# ------------------------------
# Load data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")
    return df

df = load_data()

# Guarantee list ordering stability
names = df["full_name"].tolist()

# ------------------------------
# Sidebar – full list clickable
# ------------------------------
st.sidebar.title("Physicians")

if "index" not in st.session_state:
    st.session_state.index = 0

# clickable list
for i, name in enumerate(names):
    selected = (i == st.session_state.index)
    label = f"👉 {name}" if selected else name

    if st.sidebar.button(label, key=f"name_{i}"):
        st.session_state.index = i

# Navigation buttons
col_nav1, col_nav2 = st.columns([1, 1])
if col_nav1.button("← Previous"):
    st.session_state.index = (st.session_state.index - 1) % len(df)
if col_nav2.button("Next →"):
    st.session_state.index = (st.session_state.index + 1) % len(df)

# Current row
row = df.iloc[st.session_state.index]

st.title(row.full_name)

# ------------------------------
# 3-column compact layout
# ------------------------------
col1, col2, col3 = st.columns(3)

def render_work_experience(col, row):
    col.subheader("👨‍⚕️ Work Experience")
    if pd.isna(row.work_experience_json) or row.work_experience_json.strip() == "[]":
        col.write("N/A")
        return

    try:
        import ast
        items = ast.literal_eval(row.work_experience_json)
    except:
        col.write("N/A")
        return

    for exp in items:
        col.markdown(f"**{exp.get('employer','')} — {exp.get('role','')}**")
        if exp.get("start") or exp.get("end"):
            col.write(f"{exp.get('start','')} → {exp.get('end','')}")
        if exp.get("location"):
            col.write(exp["location"])
        for src in exp.get("source", []):
            col.markdown(f"- [{src}]({src})")
        col.markdown("---")


def render_residency(col, row):
    col.subheader("🏥 Residency")
    try:
        import ast
        items = ast.literal_eval(row.residency_json)
    except:
        items = []

    if not items:
        col.write("N/A")
        return

    for r in items:
        col.markdown(f"**{r.get('institution','')}**")
        col.write(f"{r.get('start_year','')} → {r.get('end_year','')}")
        for src in r.get("source", []):
            col.markdown(f"- [{src}]({src})")
        col.markdown("---")


def render_school(col, row):
    col.subheader("🎓 Medical School")
    try:
        import ast
        items = ast.literal_eval(row.medical_school_json)
    except:
        items = []

    if not items:
        col.write("N/A")
        return

    for m in items:
        col.markdown(f"**{m.get('school','')}**")
        col.write(f"{m.get('start_year','')} → {m.get('end_year','')}")
        for src in m.get("source", []):
            col.markdown(f"- [{src}]({src})")
        col.markdown("---")


render_work_experience(col1, row)
render_residency(col2, row)
render_school(col3, row)

# ------------------------------
# Additional Details (horizontal)
# ------------------------------
st.markdown("---")
st.subheader("Additional Details")
colA, colB, colC, colD, colE = st.columns(5)

# NPI
npi_url = f"https://npiregistry.cms.hhs.gov/registry/search?number={row.NPI}"
colA.markdown("### NPI")
colA.markdown(f"[{row.NPI}]({npi_url})")

# Doximity
colB.markdown("### Doximity")
if pd.notna(row.doximity_url) and row.doximity_url != "nan":
    colB.markdown(f"[{row.doximity_url}]({row.doximity_url})")
else:
    colB.write("N/A")

# LinkedIn
colC.markdown("### LinkedIn")
if pd.notna(row.linkedin_url) and row.linkedin_url != "nan":
    colC.markdown(f"[{row.linkedin_url}]({row.linkedin_url})")
else:
    colC.write("N/A")

# Emails
colD.markdown("### Emails")
try:
    import ast
    emails = ast.literal_eval(row.emails_json)
except:
    emails = []

if emails:
    for e in emails:
        colD.markdown(f"- **{e.get('email','')}** ({e.get('type','')})")
else:
    colD.write("N/A")

# Insurance
colE.markdown("### Insurance")
try:
    insurance = ast.literal_eval(row.insurance_json)
except:
    insurance = []

if insurance:
    for ins in insurance:
        colE.markdown(f"- {ins.get('insurance','')}")
else:
    colE.write("N/A")
