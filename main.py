import streamlit as st
import streamlit as st
st.set_page_config(
    page_title="M&A Integration Copilot",
    page_icon="🧩",
    layout="wide"
)
# This is a comment for test
BRAND_CSS = """
<style>
/* Global look */
:root { --brand:#3b82f6; --ink:#0f172a; --muted:#64748b; --card:#0b1220; --border:#1f2937; }
.block-container { padding-top: 1.2rem; max-width: 1280px; }
[data-testid="stSidebar"] { background: #0a0f1a; border-right: 1px solid var(--border); }
h1,h2,h3,h4 { color: #e5e7eb !important; letter-spacing: .3px; }
body, p, li, label, span, .stTextInput label { color: #cbd5e1 !important; }

/* “cards” */
.card {
  background: linear-gradient(180deg, rgba(59,130,246,.10), rgba(59,130,246,.04));
  border: 1px solid var(--border); border-radius: 16px; padding: 18px 18px;
  box-shadow: 0 2px 14px rgba(2,6,23,.25);
}
.kpi {
  display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:14px;
  border:1px dashed #334155; background:#0b1220;
}
.badge {
  display:inline-block; padding:4px 10px; border-radius:999px;
  background:#111827; border:1px solid #374151; color:#e5e7eb; font-size:.78rem;
}
/* buttons */
.stButton>button {
  border-radius:12px !important; border:1px solid #1f2937 !important;
  transition: transform .06s ease; font-weight:600;
}
.stButton>button:hover { transform: translateY(-1px); }

/* progress label */
[data-testid="stProgressBar"] > div > div { background: var(--brand); }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# Brand header
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("### 🧩 **M&A Integration Copilot**")
    st.caption("Playbooks · Cost Merge · Readiness · Invoice Parsing · RAG")
with col2:
    st.markdown('<div style="text-align:right" class="badge">Demo build • v0.2</div>', unsafe_allow_html=True)


from modules import (
    playbook_generator,
    cost_merge_tool,
    data_migration_checker,
    invoice_parser,
    ai_assistant,
)

st.set_page_config(page_title="M&A AI Toolkit", layout="wide")

# ---- Sidebar
st.sidebar.title("🧠 M&A AI Toolkit")
st.sidebar.image("assets/Logo_Image.png", use_container_width=True)
st.sidebar.markdown("#### Navigation")

module = st.sidebar.radio(
    "Select a Module",
    (
        "Integration Playbook Generator",
        "Cost Merge Tool",
        "Data Migration Readiness Checker",
        "Invoice Parser",
        "AI M&A Assistant",
    ),
    index=0,
)

st.sidebar.caption("Built by Vamshi • Powered by GPT")
with st.sidebar.expander("About this demo", expanded=False):
    st.markdown("""
- **Agent-ready**: batches, validations, logs  
- **RAG-enabled**: knowledge-backed answers  
- **Export pack**: MD/DOCX/CSV/ZIP  
""")


# ---- Router
if module == "Integration Playbook Generator":
    playbook_generator.render()

elif module == "Cost Merge Tool":
    cost_merge_tool.render()

elif module == "Data Migration Readiness Checker":
    data_migration_checker.render()

elif module == "Invoice Parser":
    invoice_parser.render()

elif module == "AI M&A Assistant":
    ai_assistant.render()
