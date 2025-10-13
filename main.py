from pathlib import Path
import streamlit as st
import json
from streamlit_lottie import st_lottie

# --- Page background helpers (scoped & safe) ---
def set_full_dark_launch_bg():
    # Full-bleed dark background ONLY on the launch page
    st.markdown("""
    <style>
      /* Darken the whole center pane */
      html, body, [data-testid="stAppViewContainer"] { background: #0b1220 !important; }
      .block-container { background: transparent !important; }

      /* DO NOT override all text globally (keeps other pages crisp). */
      /* Style just the launch hero elements for readability on dark: */
      .launch-hero, .launch-hero * {
        color: #e5e7eb !important;   /* light text inside the hero only */
      }
      .launch-hero .launch-sub { color: #cbd5e1 !important; opacity: 0.95; }

      /* Buttons on dark */
      .launch-hero .stButton>button {
        background:#0f172a !important; color:#e5e7eb !important; border:1px solid #1f2937 !important;
      }
      .launch-hero .stButton>button:hover { transform: translateY(-1px); }
    </style>
    """, unsafe_allow_html=True)

def reset_default_bg():
    # Revert to theme/auto background AND restore theme text colors explicitly
    st.markdown("""
    <style>
      html, body, [data-testid="stAppViewContainer"] { background: none !important; }
      .block-container { background: none !important; }
      /* Explicitly restore theme-driven colors so nothing looks faded */
      h1,h2,h3,h4 { color: var(--heading) !important; }
      body, p, li, label, span, .stTextInput label, .stMarkdown, .stText {
        color: var(--text) !important; opacity: 1 !important;
      }
    </style>
    """, unsafe_allow_html=True)



def load_lottie(path: Path):
    """Safely load a local Lottie JSON file."""
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load Lottie file: {e}")
    return None


# ===== App Meta / Layout =====
st.set_page_config(
    page_title="M&A Integration Assistant",
    page_icon="🧩",
    layout="wide"
)

APP_ROOT = Path(__file__).parent
LOGO_PATH = APP_ROOT / "assets" / "logo.png"

# ===== Global Brand CSS =====
# === Theme Manager: Dark / Light / Auto (system) ===
THEME_CSS = """
<style>
/* Base variables (used if no data-theme attr is set) */
:root {
  --brand:#3b82f6; --ink:#0f172a; --muted:#94a3b8; --card:#0b1220; --border:#1f2937;
  --text:#cbd5e1; --heading:#e5e7eb; --sidebar-bg:#0a0f1a; --chip:#0b1220;
}

/* Light palette */
:root[data-theme="light"] {
  --brand:#2563eb; --ink:#0b1220; --muted:#475569; --card:#ffffff; --border:#e5e7eb;
  --text:#0f172a; --heading:#0b1220; --sidebar-bg:#f8fafc; --chip:#f1f5f9;
}

/* Dark palette */
:root[data-theme="dark"] {
  --brand:#3b82f6; --ink:#0f172a; --muted:#94a3b8; --card:#0b1220; --border:#1f2937;
  --text:#cbd5e1; --heading:#e5e7eb; --sidebar-bg:#0a0f1a; --chip:#0b1220;
}

/* When Auto is chosen, honor system preference */
@media (prefers-color-scheme: light) {
  :root:not([data-theme]) {
    --brand:#2563eb; --ink:#0b1220; --muted:#475569; --card:#ffffff; --border:#e5e7eb;
    --text:#0f172a; --heading:#0b1220; --sidebar-bg:#f8fafc; --chip:#f1f5f9;
  }
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --brand:#3b82f6; --ink:#0f172a; --muted:#94a3b8; --card:#0b1220; --border:#1f2937;
    --text:#cbd5e1; --heading:#e5e7eb; --sidebar-bg:#0a0f1a; --chip:#0b1220;
  }
}

/* Global look using variables */
.block-container { padding-top: 1.2rem; max-width: 1280px; }
[data-testid="stSidebar"] { background: var(--sidebar-bg); border-right: 1px solid var(--border); }
h1,h2,h3,h4 { color: var(--heading) !important; letter-spacing: .3px; }
body, p, li, label, span, .stTextInput label { color: var(--text) !important; }

/* Cards / KPIs */
.card {
  background: linear-gradient(180deg, color-mix(in oklab, var(--brand) 12%, transparent), color-mix(in oklab, var(--brand) 5%, transparent));
  border: 1px solid var(--border); border-radius: 16px; padding: 18px 18px; margin:.5rem 0;
  box-shadow: 0 2px 14px color-mix(in oklab, var(--ink) 25%, transparent);
}
.kpi {
  display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:14px;
  border:1px dashed color-mix(in oklab, var(--ink) 35%, transparent);
  background: var(--chip);
}

/* Badges & buttons */
.badge {
  display:inline-block; padding:6px 12px; border-radius:999px;
  background: color-mix(in oklab, var(--brand) 18%, transparent);
  border:1px solid var(--border); color: var(--heading); font-weight:600; font-size:.82rem;
}
.stButton>button {
  border-radius:12px !important; border:1px solid var(--border) !important;
  transition: transform .06s ease; font-weight:600;
}
.stButton>button:hover { transform: translateY(-1px); }
[data-testid="stProgressBar"] > div > div { background: var(--brand); }
</style>
"""

THEME_JS = """
<script>
(function() {
  // Expect a global desired theme string injected below (auto|dark|light).
  const desired = window.__MNA_THEME_PREFERENCE__;
  const root = document.documentElement;

  function applyTheme(pref) {
    if (!pref || pref === "auto") {
      // Remove override so prefers-color-scheme takes effect
      root.removeAttribute("data-theme");
    } else if (pref === "dark") {
      root.setAttribute("data-theme", "dark");
    } else if (pref === "light") {
      root.setAttribute("data-theme", "light");
    }
  }

  applyTheme(desired);

  // If Auto, listen for OS theme changes and adapt live
  if (!desired || desired === "auto") {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    mql.addEventListener("change", () => applyTheme("auto"));
  }
})();
</script>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)



# ===== Sidebar (logo + nav + about) =====
APP_ROOT = Path(__file__).parent
LOGO_PATH = APP_ROOT / "assets" / "Logo_Image.png"

if LOGO_PATH.exists():
    # ✅ Your actual company logo
    st.sidebar.image(str(LOGO_PATH), width='stretch')
else:
    # ✅ Fallback SVG if logo file not found
    st.sidebar.markdown(
        """
        <svg viewBox="0 0 420 120" width="100%" xmlns="http://www.w3.org/2000/svg">
          <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#60a5fa"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient></defs>
          <rect rx="16" ry="16" x="0" y="0" width="420" height="120" fill="var(--sidebar-bg)" stroke="var(--border)"/>
          <g transform="translate(20,30)">
            <circle cx="30" cy="30" r="26" fill="url(#g)"/>
            <text x="72" y="38" fill="var(--heading)" font-family="Inter, Segoe UI, Arial" font-size="26" font-weight="700">
              M&amp;A Integration Assistant
            </text>
          </g>
        </svg>
        """,
        unsafe_allow_html=True,
    )


st.sidebar.markdown("#### Navigation")
module = st.sidebar.radio(
    "Go to",
    (
        "Home (Launch)",               # ← NEW
        "Integration Playbook Generator",
        "Cost Synergy Estimator",
        "Data Migration Readiness Checker",
        "Invoice Parser",
        "AI M&A Assistant",
    ),
    label_visibility="collapsed",
    key="nav",                         # ← so we can programmatically switch
)


# === Theme selector ===
if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Auto"

choice = st.sidebar.radio("Theme", ["Auto", "Dark", "Light"], index=["Auto","Dark","Light"].index(st.session_state.theme_choice))
if choice != st.session_state.theme_choice:
    st.session_state.theme_choice = choice

# Inject the selection into JS (so it can set data-theme)
js_pref = {
    "Auto": "auto",
    "Dark": "dark",
    "Light": "light",
}[st.session_state.theme_choice]

st.markdown(f"<script>window.__MNA_THEME_PREFERENCE__ = '{js_pref}';</script>", unsafe_allow_html=True)
st.markdown(THEME_JS, unsafe_allow_html=True)


# Global dataset capture toggle (affects all modules)
if "capture_outputs" not in st.session_state:
    st.session_state.capture_outputs = True
st.sidebar.checkbox(
    "Save outputs to dataset (JSONL)",
    value=st.session_state.capture_outputs,
    key="capture_outputs"
)

with st.sidebar.expander("About this demo", expanded=False):
    st.markdown(
        """
- **Agent-ready**: batching, validations, logs  
- **RAG-enabled**: knowledge-backed answers (via optional backend)  
- **Export pack**: MD / DOCX / CSV / ZIP  
- **Privacy-aware**: runs with your API key  
        """
    )

# ===== Brand Header (top of main page) =====
col1, col2 = st.columns([0.78, 0.22])
with col1:
    st.markdown("### 🧩 **M&A Integration Assistant**")
    st.caption("Playbooks · Cost Merge · Readiness · Invoice Parsing · RAG")
with col2:
    st.markdown('<div style="text-align:right" class="badge">Demo build • v0.2</div>', unsafe_allow_html=True)

# ===== Demo Checklist (helpful for your live run) =====
#with st.expander("👟 Demo checklist (quick script)", expanded=False):
#    st.markdown(
#        """
#1. **Playbook → Advanced**: paste 25–50 apps → generate → open **Sources used** → download **DOCX** and **ZIP**.  
#2. **Cost Merge**: upload Buyer/Target sample CSVs → show KPIs → download merged CSV + pack.  
#3. **Readiness**: upload a source extract → show **score** + profile → export.  
#4. **Assistant**: ask “Generate Day-1 IT controls for Finance & Payroll” → point to citations.  
#        """
#    )
# ---- Lottie loader helper ----

def render_launch():
    # (Optional) if you want full dark background for the whole center pane:
    # set_full_dark_launch_bg()

    st.markdown("""
    <style>
      /* Hero container */
      .launch-hero {
        position: relative;
        border-radius: 180px;
        padding: 6px 4px;
        margin-top: .6rem;
        border: 1px solid var(--border);
        background: var(--card);
        box-shadow: 0 10px 28px color-mix(in oklab, var(--ink) 2%, transparent);
      }

      /* Headline + subhead with strong contrast */
      .launch-headline {
        font-size: clamp(28px, 5vw, 44px);
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: .2px;
        color: var(--heading);              /* high-contrast text */
        margin: 0 0 8px 0;
      }
      .launch-sub {
        font-size: 15.5px;
        margin-top: 12px;
        color: var(--text);                 /* readable body color */
        opacity: 1;                         /* ensure NOT faded */
      }

      /* CTA buttons */
      .cta-row { display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }
      .cta-row .stButton>button {
        padding:10px 14px; border-radius:12px; font-weight:700;
        border:1px solid var(--border); background: var(--card); color: var(--heading);
      }
      .cta-row .stButton>button:hover { transform: translateY(-1px); }

      /* Info box with the 3 chips grouped */
      .info-box {
        margin-top: 22px;
        padding: 18px 10px;
        border-radius: 18px;
        border: 1px solid var(--border);
        background: linear-gradient(180deg,
          color-mix(in oklab, var(--brand) 92%, transparent),
          color-mix(in oklab, var(--brand) 95%, transparent));
        box-shadow: 0 6px 240px color-mix(in oklab, var(--ink) 15%, transparent);
      }
      .info-box-title {
        font-weight: 700; font-size: 20px; color: var(--heading);
        margin-bottom: 8px; letter-spacing: .2px;margin-top: 22px;
      }
      .info-box-sub {
        font-size: 13px; color: var(--muted); margin-bottom: 14px;
      }
      .info-kpi {
        margin-top: 22px;
        text-align: center;
        padding: 10px 14px;
        border-radius: 14px;
        border: 1px dashed color-mix(in oklab, var(--ink) 35%, transparent);
        background: color-mix(in oklab, var(--brand) 6%, var(--card));
        font-size: 13px; line-height: 1.3; color: var(--heading);
        box-shadow: inset 0 1px 3px color-mix(in oklab, var(--ink) 8%, transparent);
      }

      /* --- KILL any leftover decorative bar from older versions --- */
      .glassbar, .glow, .headline::before, .launch-headline::before { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Two columns: content (left) | animation (right)
    left, right = st.columns([0.54, 0.46], vertical_alignment="center")

    with left:
        #st.markdown('<div class="launch-hero">', unsafe_allow_html=True)

        st.markdown('<div class="launch-headline">Your AI Assistant for<br/>M&A IT Integration</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="launch-sub">Generate integration playbooks, merge costs, assess data readiness, parse invoices — '
            'all knowledge-backed, export-ready, and private.</div>',
            unsafe_allow_html=True
        )

        # CTAs to jump to modules
        #st.markdown('<div class="cta-row">', unsafe_allow_html=True)
        #c1, c2, c3 = st.columns([1,1,1])
        #with c1:
        #    if st.button("🚀 Start with Playbook"):
        #        st.session_state.nav = "Integration Playbook Generator"; st.rerun()
        #with c2:
        #    if st.button("💸 Cost Merge"):
        #        st.session_state.nav = "Cost Merge Tool"; st.rerun()
        #with c3:
        #    if st.button("🚦 Readiness"):
        #        st.session_state.nav = "Data Migration Readiness Checker"; st.rerun()
        #st.markdown('</div>', unsafe_allow_html=True)

        # === Info box with grouped credibility chips ===
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown('<div class="info-box-title">✨ Key features of your AI Assistant</div>', unsafe_allow_html=True)
        #st.markdown('<div class="launch-headline">Key features of your AI Assistant</div>', unsafe_allow_html=True)
        #st.markdown('<div class="info-box-title">Every module combines:</div>', unsafe_allow_html=True)
        st.markdown('<div class="launch-sub"> ✨ Automation</div>', unsafe_allow_html=True)
        st.markdown('<div class="launch-sub"> ✨ Context awareness</div>', unsafe_allow_html=True)
        st.markdown('<div class="launch-sub"> ✨ Enterprise-grade data privacy.</div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown('<div class="info-kpi">🧠<br><b>RAG-backed</b><br>Contextual answers</div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="info-kpi">📦<br><b>Exports</b><br>DOCX / ZIP / CSV</div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="info-kpi">🔐<br><b>Private</b><br>Your API · Your data</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # /launch-hero

    with right:
        lottie_path = APP_ROOT / "assets" / "lottie" / "mna_launch.json"
        ani = load_lottie(lottie_path)
        if ani:
            st_lottie(ani, key="launch_lottie", height=420, speed=0.9, loop=True, quality="high")
        else:
            st.markdown("""
            <svg viewBox="0 0 600 420" width="100%" height="420" xmlns="http://www.w3.org/2000/svg">
              <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#60a5fa"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
              <rect width="100%" height="100%" rx="16" fill="var(--card)" stroke="var(--border)"/>
              <g transform="translate(80,90)" fill="none" stroke="url(#g1)" stroke-width="2">
                <circle cx="40" cy="40" r="22"><animate attributeName="r" values="18;26;18" dur="5s" repeatCount="indefinite"/></circle>
                <circle cx="220" cy="40" r="22"><animate attributeName="r" values="22;16;22" dur="5s" repeatCount="indefinite"/></circle>
                <circle cx="400" cy="40" r="22"><animate attributeName="r" values="20;28;20" dur="5s" repeatCount="indefinite"/></circle>
                <polyline points="62,40 200,40 242,40 380,40" opacity=".75">
                  <animate attributeName="points"
                    values="62,40 200,40 242,40 380,40;62,62 200,18 242,62 380,18;62,40 200,40 242,40 380,40"
                    dur="6s" repeatCount="indefinite"/>
                </polyline>
              </g>
              <text x="80" y="300" fill="var(--heading)" font-size="20" font-weight="700" font-family="Inter, Segoe UI, Arial">
                Merging Systems. Aligning Data. Delivering Day-1.
              </text>
            </svg>
            """, unsafe_allow_html=True)


# ===== Import & Route Modules =====
from modules import (
    playbook_generator,
    cost_merge_tool,
    data_migration_checker,
    invoice_parser,
    ai_assistant,
)

if module == "Home (Launch)":
    render_launch()

elif module == "Integration Playbook Generator":
    reset_default_bg()
    playbook_generator.render()

elif module == "Cost Synergy Estimator":
    reset_default_bg()
    cost_merge_tool.render()

elif module == "Data Migration Readiness Checker":
    reset_default_bg()
    data_migration_checker.render()

elif module == "Invoice Parser":
    reset_default_bg()
    invoice_parser.render()

elif module == "AI M&A Assistant":
    reset_default_bg()
    ai_assistant.render()

