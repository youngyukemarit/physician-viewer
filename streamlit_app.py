import streamlit as st
import pandas as pd
import ast

# -------------------------------
# Load Cleaned Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("enrichment_clean.csv")

    # Parse JSON-like fields safely
    json_cols = [
        "cleaned.work_experience",
        "cleaned.residency",
        "cleaned.medical_school",
        "cleaned.emails",
        "cleaned.insurance_accepted"
    ]

    def safe_parse(x):
        if pd.isna(x) or x == "" or x == "N/A":
            return []
        try:
            return ast.literal_eval(x)
        except Exception:
            return []

    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_parse)

    return df


df = load_data()

# -------------------------------
# Prepare dropdown list
# -------------------------------
if "cleaned.name" not in df.columns:
    st.error("Column 'cleaned.name' not found in CSV.")
    st.stop()

physician_list = sorted(df["cleaned.name"].tolist())
name_to_index = {name: i for i, name in enumerate(physician_list)}

# -------------------------------
# Session State for navigation
# -------------------------------
if "physician_index" not in st.session_state:
    st.session_state.physician_index = 0

def select_by_index(i):
    st.session_state.physician_index = i

# -------------------------------
# UI - Title
# -------------------------------
st.title("📘 Physician Profile Viewer")

# -------------------------------
# Dropdown (narrower)
# -------------------------------
col_dropdown = st.columns([1, 2, 1])[1]

selected_name = col_dropdown.selectbox(
    "Choose Physician:",
    physician_list,
    index=st.session_state.physician_index,
    key="dropdown_select"
)

# Sync dropdown → session index
st.session_state.physician_index = name_to_index[selected_name]

# -------------------------------
# Next / Previous Buttons (Top Right)
# -------------------------------
nav_col = st.columns([8, 1, 1])
if nav_col[1].button("⬅ Prev"):
    st.session_state.physician_index = (st.session_state.physician_index - 1) % len(physician_list)
    st.rerun()

if nav_col[2].button("Next ➡"):
    st.session_state.physician_index = (st.session_state.physician_index + 1) % len(physician_list)
    st.rerun()

# -------------------------------
# Pull row for display
# -------------------------------
row = df.iloc[st.session_state.physician_index]

st.header(row["cleaned.name"])

# --------------------------------------------------------
# Helper to render sections with nicer formatting
# --------------------------------------------------------
def render_section(title, items):
    st.subheader(title)
    if not items:
        st.write("N/A")
        return

    # Each item is a dict
    for item in items:
        lines = []
        for k, v in item.items():
            if k == "source":
                continue
            if v not in ["", None, "N/A"]:
                lines.append(f"**{k.capitalize()}:** {v}")

        st.write(" • " + " — ".join(lines))

        # Show sources
        if "source" in item and item["source"]:
            for link in item["source"]:
                st.markdown(f"- [{link}]({link})")

    st.markdown("---")


# -------------------------------
# Row of 3 main columns
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    render_section("💼 Work Experience", row["cleaned.work_experience"])

with col2:
    render_section("👨‍⚕️ Residency", row["cleaned.residency"])

with col3:
    render_section("🎓 Medical School", row["cleaned.medical_school"])

# -------------------------------
# Details Section
# -------------------------------
st.markdown("### Details")

with st.container():
    st.write(f"**NPI:** {row['cleaned.npi']}")

    # Emails
    emails = row["cleaned.emails"]
    if emails:
        st.write("**Emails:**")
        for e in emails:
            st.write(f"- {e.get('email', 'N/A')} ({e.get('type','')})")
    else:
        st.write("**Emails:** N/A")

    # Insurance
    ins = row["cleaned.insurance_accepted"]
    if ins:
        st.write("**Insurance:**")
        for i in ins:
            st.write(f"- {i.get('insurance','N/A')}")
    else:
        st.write("**Insurance:** N/A")

    # LinkedIn
    linkedin = row.get("cleaned.linkedin_url.url", "N/A")
    st.write(f"**LinkedIn:** {linkedin if linkedin != 'N/A' else 'N/A'}")

    # Doximity
    dox = row.get("cleaned.doximity_url.url", "N/A")
    if dox and dox != "N/A":
        st.write(f"**Doximity:** [{dox}]({dox})")
    else:
        st.write("**Doximity:** N/A")
