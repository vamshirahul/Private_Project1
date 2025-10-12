import streamlit as st
from typing import List, Dict

st.set_page_config(
    page_title="M&A AI Toolkit",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "nav_module" not in st.session_state:
    st.session_state["nav_module"] = "Home"
if "sidebar_collapsed" not in st.session_state:
    st.session_state["sidebar_collapsed"] = False

ICONS = {
    "Integration Playbook Generator": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>""",
    "Cost Merge Tool": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>""",
    "Data Migration Readiness Checker": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>""",
    "Invoice Parser": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="m10 13-2 2 2 2"></path><path d="m14 13 2 2-2 2"></path></svg>""",
    "AI M&A Assistant": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"></path><rect x="4" y="12" width="8" height="8" rx="2"></rect><path d="M8 12v-2a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2"></path><path d="M16 12h-2a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h2"></path></svg>""",
}

NAV_ITEMS: List[Dict[str, str]] = [
    {"name": "Home", "icon": "🏠", "hint": "Go to landing"},
    {"name": "Integration Playbook Generator", "icon": ICONS["Integration Playbook Generator"], "hint": "Design integration playbooks"},
    {"name": "Cost Merge Tool", "icon": ICONS["Cost Merge Tool"], "hint": "Cost synergy modeling"},
    {"name": "Data Migration Readiness Checker", "icon": ICONS["Data Migration Readiness Checker"], "hint": "Assess data readiness"},
    {"name": "Invoice Parser", "icon": ICONS["Invoice Parser"], "hint": "Parse and structure invoices"},
    {"name": "AI M&A Assistant", "icon": ICONS["AI M&A Assistant"], "hint": "Ask questions with RAG"},
]

ENHANCED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
:root {
    --bg: #0a0f1a; --ink: #e5e7eb; --border: #1f2937; --card-bg: #0b1220;
    --brand-400: #60a5fa; --brand-600: #2563eb; --font-family: 'Poppins', sans-serif;
}
html, body { background: var(--bg); }
.block-container { max-width: 1280px; padding-top: 2rem; }
h1,h2,h3,h4 { color: var(--ink) !important; font-family: var(--font-family); font-weight: 700; }
h1:hover .anchor { display: none; }
body, p, li, label, span, .stTextInput label, .stMarkdown { color: #cbd5e1 !important; font-family: var(--font-family); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(11,18,32,1), rgba(10,15,26,.92));
    border-right: 1px solid var(--border);
}

.nav-buttons-container {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

.nav-menu { display: flex; flex-direction: column; gap: 4px; }
.nav-item {
    display: flex; align-items: center; gap: 10px; cursor: pointer;
    padding: 8px 10px; border-radius: 12px; border: 1px solid transparent;
    transition: background 0.15s ease, transform 0.08s ease;
}
.nav-item:hover { background: #0f172a; transform: translateX(2px); border-color: var(--border); }
.nav-item.active { background: var(--brand-600); color: white !important; border-color: var(--brand-400); }
.nav-item svg { width: 20px; height: 20px; stroke: #cbd5e1; }
.nav-item.active svg { stroke: white; }
.nav-item p { color: #cbd5e1 !important; margin-bottom: 0; }
.nav-item.active p { color: white !important; }

.card {
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 24px;
    box-shadow: 0 6px 18px rgba(2,6,23,.35);
    transition: transform .15s ease, box-shadow .15s ease, background .2s ease;
    display: flex; flex-direction: column; height: 100%;
}
.card:hover { transform: translateY(-3px); box-shadow: 0 10px 26px rgba(2,6,23,.45); }
.card-icon { color: var(--brand-400); margin-bottom: 0.75rem; }
.card-icon svg { width: 36px; height: 36px; }
.card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: .25rem; }
.card-desc { font-size: 0.95rem; color: #94a3b8; flex-grow: 1; }
.card .stButton>button {
    border-radius:12px !important; border:1px solid #1f2937 !important; font-weight:600; margin-top: 1rem;
    background: linear-gradient(180deg, rgba(30,58,138,.65), rgba(30,58,138,.35));
}
.card .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 0 0 3px rgba(59,130,246,.25); }
</style>
"""
st.markdown(ENHANCED_CSS, unsafe_allow_html=True)

from modules import (
    playbook_generator, cost_merge_tool, data_migration_checker,
    invoice_parser, ai_assistant
)

st.sidebar.title("🧠 M&A AI Toolkit")
st.sidebar.image("assets/Logo_Image.png", use_container_width=True)
st.sidebar.markdown("---")

for item in NAV_ITEMS:
    if st.sidebar.button(item["name"], key=f"btn_{item['name']}", use_container_width=True):
        st.session_state["nav_module"] = item["name"]
        st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander("About this demo", expanded=False):
    st.markdown("""
- **Agent-ready**: batches, validations, logs
- **RAG-enabled**: knowledge-backed answers
- **Export pack**: MD/DOCX/CSV/ZIP
""")

def hero():
    st.markdown(
        """
        <div style="animation:fadeIn .25s ease both">
            <h1 style="margin-bottom:.25rem">M&A Integration Copilot</h1>
            <p style="color:#94a3b8; font-size:1.05rem;">A suite of AI-powered tools to streamline your M&A workflow.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("---")
    cards = [
        ("Integration Playbook Generator", ICONS["Integration Playbook Generator"], "Design bespoke playbooks, templates, and workstreams."),
        ("Cost Merge Tool", ICONS["Cost Merge Tool"], "Model synergies, OPEX/CAPEX impacts, and future-state scenarios."),
        ("Data Migration Readiness Checker", ICONS["Data Migration Readiness Checker"], "Utilize checklists, identify risks, and manage data gates."),
        ("Invoice Parser", ICONS["Invoice Parser"], "Automatically extract, normalize, and export data from invoices."),
        ("AI M&A Assistant", ICONS["AI M&A Assistant"], "Ask complex, knowledge-backed questions using Retrieval-Augmented Generation."),
    ]
    cols = st.columns(3)
    for i, (name, icon, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{name}</div>
                    <div class="card-desc">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Launch Module", key=f"card_{i}", use_container_width=True):
                st.session_state["nav_module"] = name
                st.rerun()

if st.session_state["nav_module"] == "Home":
    hero()
else:
    st.markdown('<div style="animation:fadeIn .25s ease both">', unsafe_allow_html=True)
    module_name = st.session_state["nav_module"]
    if module_name == "Integration Playbook Generator": playbook_generator.render()
    elif module_name == "Cost Merge Tool": cost_merge_tool.render()
    elif module_name == "Data Migration Readiness Checker": data_migration_checker.render()
    elif module_name == "Invoice Parser": invoice_parser.render()
    elif module_name == "AI M&A Assistant": ai_assistant.render()
    st.markdown('</div>', unsafe_allow_html=True)