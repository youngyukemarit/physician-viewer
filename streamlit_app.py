# streamlit_app.py
import streamlit as st
import pandas as pd
import ast
import json
from typing import Any, Dict, List, Optional, Union

# -----------------------------
# Page + Light UI
# -----------------------------
st.set_page_config(
    page_title="Physician Profile Viewer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LIGHT_CSS = """
<style>
/* overall */
.stApp {
  background: #ffffff !important;
  color: #111827 !important;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}
h1, h2, h3, h4, h5, h6, p, li, span, div { color: #111827 !important; }

/* top spacing */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1200px; }

/* cards */
.section-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 12px;
}
.section-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #111827;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* links */
a { color: #2563eb !important; text-decoration: none; }
a:hover { text-decoration: underline; }

/* selectbox width */
div[data-baseweb="select"] { max-width: 460px !important; }

/* buttons nicer */
.stButton>button {
  border-radius: 10px !important;
  padding: 0.45rem 0.75rem !important;
  border: 1px solid #d1d5db !important;
  background: #ffffff !important;
  color: #111827 !important;
  font-weight: 600 !important;
}
.stButton>button:hover {
  border-color: #9ca3af !important;
  background: #f9fafb !important;
}

/* remove dark margins */
hr { border-top: 1px solid #e5e7eb; }
</style>
"""
st.markdown(LIGHT_CSS, unsafe_allow_html=True)


# -----------------------------
# Helpers
# -----------------------------
def safe_parse(x: Any) -> Any:
    """Parse list/dict stored as string. Never throw."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    if isinstance(x, (list, dict)):
        return x
    s = str(x).strip()
    if s == "" or s.lower() in {"na", "n/a", "nan", "none"}:
        return []
    # try json first (sometimes single quotes break json so fallback)
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        return ast.literal_eval(s)
    except Exception:
        return []


def pick_value(row: pd.Series, cleaned_key: str, raw_key: str, default=None):
    """Prefer cleaned.* over raw.* over default."""
    for k in [cleaned_key, raw_key]:
        if k in row.index:
            v = row[k]
            if not (pd.isna(v) or str(v).strip() in {"", "nan", "None"}):
                return v
    return default


def nonempty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, float) and pd.isna(v):
        return False
    if isinstance(v, str) and v.strip().lower() in {"", "nan", "none", "n/a"}:
        return False
    if isinstance(v, list) and len(v) == 0:
        return False
    if isinstance(v, dict) and len(v) == 0:
        return False
    return True


def format_sources(sources: Any) -> str:
    """Return markdown for sources list."""
    srcs = safe_parse(sources)
    if not srcs:
        return ""
    md_links = []
    for u in srcs:
        if not u or str(u).strip() in {"N/A", "nan"}:
            continue
        md_links.append(f"[{u}]({u})")
    if not md_links:
        return ""
    return " • " + " • ".join(md_links)


def pretty_item(d: Dict[str, Any], field_order: List[str]) -> str:
    """Render one dict without confidence noise."""
    parts = []
    for k in field_order:
        if k not in d:
            continue
        v = d.get(k)
        if not nonempty(v):
            continue
        if k == "source":
            continue
        label = k.replace("_", " ").title()
        parts.append(f"**{label}:** {v}")
    # add any extra keys (except confidence/source)
    for k, v in d.items():
        if k in field_order or k in {"confidence", "source"}:
            continue
        if not nonempty(v):
            continue
        label = k.replace("_", " ").title()
        parts.append(f"**{label}:** {v}")
    base = " — ".join(parts) if parts else "N/A"
    base += format_sources(d.get("source", []))
    return base


def render_section(title: str, items: Any, field_order: List[str]):
    st.markdown(f"<div class='section-card'><div class='section-title'>{title}</div>", unsafe_allow_html=True)
    parsed = safe_parse(items)

    if not parsed:
        st.markdown("N/A")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if isinstance(parsed, dict):
        parsed = [parsed]

    for it in parsed:
        if not isinstance(it, dict):
            st.markdown(str(it))
            continue
        st.markdown(f"- {pretty_item(it, field_order)}")

    st.markdown("</div>", unsafe_allow_html=True)


def clean_url(u: Any) -> Optional[str]:
    if not nonempty(u):
        return None
    s = str(u).strip()
    if s in {"N/A", "nan"}:
        return None
    return s


# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    # prefer enrichment_clean.csv, fall back to other known names
    candidates = [
        "enrichment_clean.csv",
        "profile_enrichment_export.csv",
        "profile_enrichment_base44.csv",
    ]
    last_err = None
    for path in candidates:
        try:
            df_ = pd.read_csv(path)
            return df_
        except Exception as e:
            last_err = e
    raise FileNotFoundError(f"Could not load any CSV from {candidates}. Last error: {last_err}")


df = load_data()

# Normalize key columns
# create a unified name + npi column used for UI
def get_name(row):
    return (
        pick_value(row, "cleaned.name", "raw.name")
        or row.get("name")
        or row.get("full_name")
        or "Unknown"
    )

def get_npi(row):
    return (
        pick_value(row, "cleaned.npi", "raw.npi")
        or row.get("npi")
        or row.get("raw.npi")
        or ""
    )

df["__name__"] = df.apply(get_name, axis=1).astype(str)
df["__npi__"] = df.apply(get_npi, axis=1).astype(str)

# sort alphabetically by name
df = df.sort_values("__name__", kind="stable").reset_index(drop=True)

# build display labels
labels = [f"{n} — {p}" if p else n for n, p in zip(df["__name__"], df["__npi__"])]

# session state for index selection
if "idx" not in st.session_state:
    st.session_state.idx = 0


def set_idx(new_idx: int):
    st.session_state.idx = max(0, min(len(df) - 1, new_idx))


# -----------------------------
# Header Row: dropdown + prev/next inline
# -----------------------------
left, mid, right = st.columns([6, 2, 2], vertical_alignment="center")

with left:
    st.markdown("## 📘 Physician Profile Viewer")
    # selectbox returns label; map to index
    selected_label = st.selectbox(
        "Choose Physician:",
        labels,
        index=st.session_state.idx,
        key="physician_select",
    )
    # sync idx if user chooses from dropdown
    chosen_idx = labels.index(selected_label)
    if chosen_idx != st.session_state.idx:
        set_idx(chosen_idx)

with mid:
    st.write("")  # spacer
    if st.button("← Prev", use_container_width=True, disabled=(st.session_state.idx == 0)):
        set_idx(st.session_state.idx - 1)
        st.rerun()

with right:
    st.write("")  # spacer
    if st.button("Next →", use_container_width=True, disabled=(st.session_state.idx >= len(df) - 1)):
        set_idx(st.session_state.idx + 1)
        st.rerun()


row = df.iloc[st.session_state.idx]

# -----------------------------
# Main Profile
# -----------------------------
name = row["__name__"]
npi = row["__npi__"]

st.markdown(f"## {name}")

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    render_section(
        "Work Experience",
        pick_value(row, "cleaned.work_experience", "raw.work_experience", default=[]),
        field_order=["employer", "role", "start", "end", "location"],
    )

with c2:
    render_section(
        "Residency",
        pick_value(row, "cleaned.residency", "raw.residency", default=[]),
        field_order=["institution", "start_year", "end_year"],
    )

with c3:
    render_section(
        "Medical School",
        pick_value(row, "cleaned.medical_school", "raw.medical_school", default=[]),
        field_order=["institution", "start_year", "end_year"],
    )

st.divider()

# -----------------------------
# Details (horizontal, compact)
# -----------------------------
d1, d2, d3, d4, d5 = st.columns(5, gap="large")

# NPI registry provider-view link
with d1:
    st.markdown("<div class='section-card'><div class='section-title'>NPI</div>", unsafe_allow_html=True)
    if nonempty(npi):
        npi_url = f"https://npiregistry.cms.hhs.gov/provider-view/{npi}"
        st.markdown(f"[{npi}]({npi_url})")
    else:
        st.markdown("N/A")
    st.markdown("</div>", unsafe_allow_html=True)

with d2:
    st.markdown("<div class='section-card'><div class='section-title'>Doximity</div>", unsafe_allow_html=True)
    dox = clean_url(pick_value(row, "cleaned.doximity_url.url", "raw.doximity_url.url"))
    if dox:
        st.markdown(f"[{dox}]({dox})")
    else:
        st.markdown("N/A")
    st.markdown("</div>", unsafe_allow_html=True)

with d3:
    st.markdown("<div class='section-card'><div class='section-title'>LinkedIn</div>", unsafe_allow_html=True)
    li = clean_url(pick_value(row, "cleaned.linkedin_url.url", "raw.linkedin_url.url"))
    if li:
        st.markdown(f"[{li}]({li})")
    else:
        st.markdown("N/A")
    st.markdown("</div>", unsafe_allow_html=True)

with d4:
    st.markdown("<div class='section-card'><div class='section-title'>Emails</div>", unsafe_allow_html=True)
    emails = safe_parse(pick_value(row, "cleaned.emails", "raw.emails", default=[]))
    if not emails:
        st.markdown("N/A")
    else:
        if isinstance(emails, dict):
            emails = [emails]
        for e in emails:
            if isinstance(e, dict):
                addr = e.get("email") or e.get("address") or "N/A"
                st.markdown(f"- {addr}{format_sources(e.get('source', []))}")
            else:
                st.markdown(f"- {e}")
    st.markdown("</div>", unsafe_allow_html=True)

with d5:
    st.markdown("<div class='section-card'><div class='section-title'>Insurance</div>", unsafe_allow_html=True)
    ins = safe_parse(pick_value(row, "cleaned.insurance_accepted", "raw.insurance_accepted", default=[]))
    if not ins:
        st.markdown("N/A")
    else:
        if isinstance(ins, dict):
            ins = [ins]
        for i in ins:
            if isinstance(i, dict):
                nm = i.get("insurance") or "N/A"
                st.markdown(f"- {nm}{format_sources(i.get('source', []))}")
            else:
                st.markdown(f"- {i}")
    st.markdown("</div>", unsafe_allow_html=True)
