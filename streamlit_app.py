import streamlit as st
import pandas as pd
import ast

# -----------------------------
# Light Theme + Page Config
# -----------------------------
st.set_page_config(
    page_title="Physician Profile Viewer",
    layout="wide",
)

# -----------------------------
# Load & Clean CSV
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Columns that contain JSON-like dicts/lists
    json_cols = [
        "work_experience",
        "residency",
        "medical_school",
        "emails",
        "insurance"
    ]

    def parse(x):
        if pd.isna(x) or x == "":
            return []
        try:
            return ast.literal_eval(x)
        except:
            return []

    for c in json_cols:
        if c in df.columns:
            df[c] = df[c].apply(parse)

    df["full_name"] = df["full_name"].fillna("Unknown")
    df = df.sort_values("full_name")
    df = df.reset_index(drop=True)
    return df

df = load_data()

# -----------------------------
# Helper functions
# -----------------------------
def render_section(title, items, fields):
    """Pretty print list of dicts."""
    st.subheader(title)
    if not items:
        st.write("N/A")
        return

    for item in items:
        for f in fields:
            value = item.get(f, "N/A")
            if value and value != "N/A":
                st.markdown(f"**{f.replace('_',' ').title()}:** {value}")
        sources = item.get("source", [])
        if sources:
            for s in sources:
                st.markdown(f"- [{s}]({s})")
        st.write("----")

def npi_link(npi):
    if not npi or npi == "N/A":
        return "N/A"
    url = f"https://npiregistry.cms.hhs.gov/registry/npi/{npi}"
    return f"[{npi}]({url})"


# -----------------------------
# Navigation State
# -----------------------------
if "index" not in st.session_state:
    st.session_state.index = 0

names = df["full_name"].tolist()

def move(delta):
    st.session_state.index = (st.session_state.index + delta) % len(df)

# -----------------------------
# UI HEADER
# -----------------------------
st.title("📘 Physician Profile Viewer")

cols = st.columns([3, 1])
with cols[0]:
    selected = st.selectbox(
        "Choose Physician:",
        names,
        index=st.session_state.index
    )

# Sync index to dropdown
st.session_state.index = names.index(selected)

with cols[1]:
    st.button("⬅ Prev", on_click=lambda: move(-1))
    st.button("Next ➡", on_click=lambda: move(1))

row = df.iloc[st.session_state.index]

# -----------------------------
# MAIN PROFILE
# -----------------------------
st.header(row["full_name"])

col1, col2, col3 = st.columns(3)

with col1:
    render_section(
        "🏢 Work Experience",
        row["work_experience"],
        ["employer", "role", "start", "end", "location"]
    )

with col2:
    render_section(
        "🧑‍⚕️ Residency",
        row["residency"],
        ["institution", "start_year", "end_year"]
    )

with col3:
    render_section(
        "🎓 Medical School",
        row["medical_school"],
        ["institution", "start_year", "end_year"]
    )

# -----------------------------
# Details Section
# -----------------------------
st.markdown("---")
st.subheader("Details")

d1, d2, d3 = st.columns(3)

with d1:
    st.markdown(f"**NPI:** {npi_link(row['npi'])}")
    st.markdown("### Emails")
    if row["emails"]:
        for e in row["emails"]:
            st.write(e.get("email", "N/A"))
    else:
        st.write("N/A")

with d2:
    st.markdown("### Insurance")
    if row["insurance"]:
        for ins in row["insurance"]:
            st.write(f"- {ins.get('insurance','N/A')}")
    else:
        st.write("N/A")

with d3:
    st.markdown("### Doximity")
    dox = row.get("doximity_url", "")
    st.write(dox if dox else "N/A")

    st.markdown("### LinkedIn")
    linked = row.get("linkedin_url", "")
    st.write(linked if linked else "N/A")
