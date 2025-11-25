import ast
from pathlib import Path
import pandas as pd
import streamlit as st

# ----------------------------
# Page + light-mode styling
# ----------------------------
st.set_page_config(
    page_title="Physician Profile Viewer",
    page_icon="📘",
    layout="wide",
)

LIGHT_CSS = """
<style>
/* Main background + text */
.stApp {
    background: #ffffff !important;
    color: #111827 !important;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;  /* keep wide but not infinite */
}

/* Headings */
h1, h2, h3, h4, h5 {
    color: #0f172a !important;
}

/* Section cards */
.section-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 14px;
}

/* Labels */
.label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: .03em;
}

/* Small muted text */
.muted {
    color: #64748b;
    font-size: 0.9rem;
}

/* Links */
a {
    color: #2563eb !important;
    text-decoration: none;
}
a:hover { text-decoration: underline; }

/* Make the selectbox not full-width */
div[data-baseweb="select"] {
    max-width: 520px;  /* you can tweak */
}

/* Make buttons look a bit cleaner */
.stButton > button {
    border-radius: 10px;
    padding: 0.45rem 0.8rem;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    color: #0f172a;
}
.stButton > button:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
}
</style>
"""
st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ----------------------------
# Helpers
# ----------------------------
def safe_parse(x):
    """Parse stringified python lists/dicts without crashing."""
    if pd.isna(x) or x == "" or x == "N/A":
        return []
    if isinstance(x, (list, dict)):
        return x
    try:
        return ast.literal_eval(str(x))
    except Exception:
        return []

def col_exists(df, name):
    return name in df.columns

@st.cache_data(show_spinner=False)
def load_data():
    # Prefer enrichment_clean.csv if present, otherwise fall back
    candidates = [
        "enrichment_clean.csv",
        "profile_enrichment_export.csv",
        "profile_enrichment_base44.csv",
    ]
    csv_path = None
    for c in candidates:
        p = Path(c)
        if p.exists():
            csv_path = p
            break
    if csv_path is None:
        raise FileNotFoundError(
            f"None of these CSVs found in repo root: {candidates}"
        )

    df = pd.read_csv(csv_path)

    # Parse only columns that exist (no KeyErrors)
    parse_cols = [
        "cleaned.work_experience", "raw.work_experience",
        "cleaned.residency", "raw.residency",
        "cleaned.medical_school", "raw.medical_school",
        "cleaned.emails", "raw.emails",
        "cleaned.insurance_accepted", "raw.insurance_accepted",
    ]
    for c in parse_cols:
        if col_exists(df, c):
            df[c] = df[c].apply(safe_parse)

    return df

def pick_value(row, *cols, default=None):
    """Return first non-null/non-empty value from cols."""
    for c in cols:
        if c in row and not pd.isna(row[c]) and str(row[c]).strip() not in ["", "nan", "None"]:
            return row[c]
    return default

def normalize_name(row):
    return (
        pick_value(row, "cleaned.name", "raw.name")
        or str(pick_value(row, "cleaned.npi", "raw.npi", "npi", default="Unknown")).strip()
        or "Unknown"
    )

def normalize_npi(row):
    return str(pick_value(row, "cleaned.npi", "raw.npi", "npi", default="N/A")).strip()

def normalize_url(row, *cols):
    v = pick_value(row, *cols, default="N/A")
    if v is None or str(v).strip() in ["", "nan", "None"]:
        return "N/A"
    return str(v).strip()

def render_sources(sources):
    if not sources:
        return ""
    # show all links inline
    links = []
    for s in sources:
        if s and str(s).strip() not in ["N/A", "nan"]:
            links.append(f"[{s}]({s})")
    return " • " + " • ".join(links) if links else ""

def render_list_section(title, items, kind):
    st.markdown(f'<div class="section-card"><div class="label">{title}</div>', unsafe_allow_html=True)
    if not items:
        st.markdown('<div class="muted">N/A</div></div>', unsafe_allow_html=True)
        return

    for it in items:
        if not isinstance(it, dict):
            st.markdown(f"- {it}")
            continue

        if kind == "work":
            employer = it.get("employer", "N/A")
            role = it.get("role", "N/A")
            start = it.get("start", "N/A")
            end = it.get("end", "N/A")
            location = it.get("location", "N/A")
            conf = it.get("confidence", "N/A")
            sources = it.get("source", [])

            st.markdown(
                f"**{employer} — {role}**  \n"
                f"{start} → {end}  \n"
                f"{location}  \n"
                f"*Confidence: {conf}*"
                f"{render_sources(sources)}"
            )

        elif kind == "edu":
            inst = it.get("institution", "N/A")
            sy = it.get("start_year", "N/A")
            ey = it.get("end_year", "N/A")
            conf = it.get("confidence", "N/A")
            sources = it.get("source", [])

            st.markdown(
                f"**{inst}**  \n"
                f"{sy} → {ey}  \n"
                f"*Confidence: {conf}*"
                f"{render_sources(sources)}"
            )
        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

def render_emails(emails):
    st.markdown('<div class="section-card"><div class="label">Emails</div>', unsafe_allow_html=True)
    if not emails:
        st.markdown('<div class="muted">N/A</div></div>', unsafe_allow_html=True)
        return

    for e in emails:
        if isinstance(e, dict):
            email = e.get("email", "N/A")
            etype = e.get("type", "N/A")
            conf = e.get("confidence", "N/A")
            sources = e.get("source", [])
            st.markdown(
                f"- **{email}** *(type: {etype}, confidence: {conf})*{render_sources(sources)}"
            )
        else:
            st.markdown(f"- {e}")
    st.markdown("</div>", unsafe_allow_html=True)

def render_insurance(ins):
    st.markdown('<div class="section-card"><div class="label">Insurance Accepted</div>', unsafe_allow_html=True)
    if not ins:
        st.markdown('<div class="muted">N/A</div></div>', unsafe_allow_html=True)
        return

    for i in ins:
        if isinstance(i, dict):
            name = i.get("insurance", "N/A")
            conf = i.get("confidence", "N/A")
            sources = i.get("source", [])
            st.markdown(f"- **{name}** *(confidence: {conf})*{render_sources(sources)}")
        else:
            st.markdown(f"- {i}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# App
# ----------------------------
df = load_data()

# Prepare labels sorted alphabetically by name
df = df.copy()
df["__name__"] = df.apply(normalize_name, axis=1)
df["__npi__"] = df.apply(normalize_npi, axis=1)
df["__label__"] = df.apply(lambda r: f"{r['__name__']} — {r['__npi__']}", axis=1)

df_sorted = df.sort_values("__name__", kind="stable").reset_index(drop=True)
labels = df_sorted["__label__"].tolist()
label_to_idx = {lab: i for i, lab in enumerate(labels)}

# Session-state selection
if "selected_index" not in st.session_state:
    st.session_state.selected_index = 0

# --- Top bar: title + dropdown + prev/next ---
top_left, top_mid, top_prev, top_next = st.columns([3.5, 2.2, 0.7, 0.7], vertical_alignment="center")

with top_left:
    st.title("📘 Physician Profile Viewer")
    st.caption("Select a physician to view enrichment results.")

with top_mid:
    selected_label = st.selectbox(
        "Choose Physician:",
        labels,
        index=st.session_state.selected_index,
        key="physician_select",
    )

# Sync index if user used dropdown
new_idx = label_to_idx[selected_label]
if new_idx != st.session_state.selected_index:
    st.session_state.selected_index = new_idx

with top_prev:
    if st.button("← Prev", use_container_width=True):
        st.session_state.selected_index = max(0, st.session_state.selected_index - 1)
        st.rerun()

with top_next:
    if st.button("Next →", use_container_width=True):
        st.session_state.selected_index = min(len(labels) - 1, st.session_state.selected_index + 1)
        st.rerun()

row = df_sorted.iloc[st.session_state.selected_index]

name = row["__name__"]
npi = row["__npi__"]

st.markdown(f"## {name}")

# Three main columns for scanning
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    work_items = pick_value(row, "cleaned.work_experience", "raw.work_experience", default=[])
    render_list_section("Work Experience", work_items, kind="work")

with c2:
    res_items = pick_value(row, "cleaned.residency", "raw.residency", default=[])
    render_list_section("Residency", res_items, kind="edu")

with c3:
    ms_items = pick_value(row, "cleaned.medical_school", "raw.medical_school", default=[])
    render_list_section("Medical School", ms_items, kind="edu")

st.markdown("---")

# Details row (compact)
details_cols = st.columns([1.2, 1.2, 1.2, 2.2], gap="large")

# NPI
with details_cols[0]:
    st.markdown('<div class="section-card"><div class="label">NPI</div>', unsafe_allow_html=True)
    if npi != "N/A":
        registry_url = f"https://npiregistry.cms.hhs.gov/provider-view/{npi}"
        st.markdown(f"[{npi}]({registry_url})")
    else:
        st.markdown('<div class="muted">N/A</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Doximity
with details_cols[1]:
    dox_url = normalize_url(row, "cleaned.doximity_url.url", "raw.doximity_url.url")
    st.markdown('<div class="section-card"><div class="label">Doximity</div>', unsafe_allow_html=True)
    st.markdown(dox_url if dox_url == "N/A" else f"[{dox_url}]({dox_url})")
    st.markdown("</div>", unsafe_allow_html=True)

# LinkedIn
with details_cols[2]:
    li_url = normalize_url(row, "cleaned.linkedin_url.url", "raw.linkedin_url.url")
    st.markdown('<div class="section-card"><div class="label">LinkedIn</div>', unsafe_allow_html=True)
    st.markdown(li_url if li_url == "N/A" else f"[{li_url}]({li_url})")
    st.markdown("</div>", unsafe_allow_html=True)

# Emails + Insurance stacked
with details_cols[3]:
    emails = pick_value(row, "cleaned.emails", "raw.emails", default=[])
    insurance = pick_value(row, "cleaned.insurance_accepted", "raw.insurance_accepted", default=[])
    render_emails(emails)
    render_insurance(insurance)
