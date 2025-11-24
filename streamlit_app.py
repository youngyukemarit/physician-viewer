import streamlit as st
import pandas as pd
import ast

# ---------------------- CONFIG ----------------------
st.set_page_config(page_title="Physician Viewer", layout="wide")


# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("profile_enrichment_base44.csv")
    return df

df = load_data()


def parse_json_field(v):
    if pd.isna(v) or v == "" or v == "[]":
        return []
    try:
        return ast.literal_eval(v)
    except:
        return []


df["work_experience"] = df["work_experience"].apply(parse_json_field)
df["residency"] = df["residency"].apply(parse_json_field)
df["medical_school"] = df["medical_school"].apply(parse_json_field)
df["insurance_accepted"] = df["insurance_accepted"].apply(parse_json_field)
df["emails"] = df["emails"].apply(parse_json_field)

physicians = sorted(df["full_name"].tolist())

# ---------------------- SIDEBAR: BEAUTIFUL CLICK LIST ----------------------

st.markdown(
    """
    <style>
        .name-item {
            padding: 10px 14px;
            cursor: pointer;
            border-radius: 6px;
            margin-bottom: 4px;
            font-size: 15px;
        }
        .name-item:hover {
            background-color: #2c2c2c;
        }
        .name-item.selected {
            background-color: #444;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("### Physicians")

    # We store selected name in session state
    if "selected_name" not in st.session_state:
        st.session_state.selected_name = physicians[0]

    clicked = None
    for name in physicians:
        css_class = "name-item"
        if name == st.session_state.selected_name:
            css_class += " selected"

        if st.markdown(
            f"<div class='{css_class}'>{name}</div>",
            unsafe_allow_html=True
        ):
            pass

        # Hack: detect click via unique key buttons
        if st.button(name, key=name, help=name):
            st.session_state.selected_name = name

selected_name = st.session_state.selected_name
record = df[df["full_name"] == selected_name].iloc[0]

# ---------------------- 3 COLUMN LAYOUT ----------------------
left, middle, right = st.columns([1, 2.2, 1.2])


# ---------------------- MIDDLE COLUMN (PRIMARY INFO) ----------------------
with middle:
    st.title(selected_name)

    # --- WORK EXPERIENCE ---
    st.subheader("🏢 Work Experience")
    if not record["work_experience"]:
        st.write("None")
    else:
        for job in record["work_experience"]:
            st.markdown(f"**{job.get('employer', '')} — {job.get('role','')}**")
            st.write(f"{job.get('start','')} → {job.get('end','')}")
            if job.get("location"):
                st.write(job["location"])
            if job.get("source"):
                for url in job["source"]:
                    st.markdown(f"- [{url}]({url})")
            st.markdown("---")

    # --- RESIDENCY ---
    st.subheader("🏥 Residency")
    if not record["residency"]:
        st.write("None")
    else:
        for r in record["residency"]:
            st.markdown(f"**{r.get('institution','')}**")
            st.write(f"{r.get('start_year','')} → {r.get('end_year','')}")
            for url in r.get("source", []):
                st.markdown(f"- [{url}]({url})")
            st.markdown("---")

    # --- MEDICAL SCHOOL ---
    st.subheader("🎓 Medical School")
    if not record["medical_school"]:
        st.write("None")
    else:
        for m in record["medical_school"]:
            st.markdown(f"**{m.get('institution','')}**")
            st.write(f"{m.get('start_year','')} → {m.get('end_year','')}")
            for url in m.get("source", []):
                st.markdown(f"- [{url}]({url})")
            st.markdown("---")


# ---------------------- RIGHT COLUMN (SECONDARY INFO) ----------------------
with right:
    st.subheader("ℹ️ Details")

    # NPI
    st.markdown(
        f"**NPI:** [{record['NPI']}](https://npiregistry.cms.hhs.gov/registry/NPI/{record['NPI']})"
    )

    # Links
    if record.get("doximity_url") not in ["", "N/A", None]:
        st.markdown(f"**Doximity:** [{record['doximity_url']}]({record['doximity_url']})")

    if record.get("linkedin_url") not in ["", "N/A", None]:
        st.markdown(f"**LinkedIn:** [{record['linkedin_url']}]({record['linkedin_url']})")

    # Emails
    st.subheader("✉️ Emails")
    if not record["emails"]:
        st.write("None")
    else:
        for e in record["emails"]:
            st.write(f"- {e}")

    # Insurance
    st.subheader("🛡 Insurance")
    if not record["insurance_accepted"]:
        st.write("None")
    else:
        for ins in record["insurance_accepted"]:
            st.write(f"- {ins.get('insurance','')}")
