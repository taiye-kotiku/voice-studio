"""
🎙️ VoiceStudio — Self-Hosted Voice Cloning Dashboard
Powered by Coqui XTTS v2 + Modal
"""

import streamlit as st

st.set_page_config(
    page_title="VoiceStudio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark theme overrides */
    .main { background-color: #0e1117; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0e1117 100%);
    }
    
    /* Cards */
    .voice-card {
        background: linear-gradient(135deg, #1e2740 0%, #16213e 100%);
        border: 1px solid #2d3561;
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    .voice-card:hover {
        border-color: #6c63ff;
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.15);
    }
    .voice-card.selected {
        border-color: #6c63ff;
        background: linear-gradient(135deg, #252a4a 0%, #1e2740 100%);
        box-shadow: 0 4px 24px rgba(108, 99, 255, 0.3);
    }

    /* Stat boxes */
    .stat-box {
        background: #1e2740;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid #2d3561;
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #6c63ff; }
    .stat-label { font-size: 0.85rem; color: #8892b0; margin-top: 4px; }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* Generate button */
    .generate-btn > button {
        background: linear-gradient(135deg, #6c63ff, #a855f7);
        color: white;
        border: none;
        padding: 14px 32px;
        font-size: 1.1rem;
        border-radius: 12px;
        width: 100%;
    }

    /* Audio player */
    audio { width: 100%; border-radius: 10px; }

    /* Tag pills */
    .tag {
        display: inline-block;
        background: #2d3561;
        color: #a0aec0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 2px;
    }
    .tag.lang { background: #1e3a5f; color: #63b3ed; }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 16px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2d3561;
    }

    /* History item */
    .history-item {
        background: #1a1f2e;
        border-left: 3px solid #6c63ff;
        border-radius: 0 10px 10px 0;
        padding: 12px 16px;
        margin: 6px 0;
    }
    
    /* Logo area */
    .logo-text {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6c63ff, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">🎙️ VoiceStudio</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;font-size:0.85rem;margin-top:-8px;">Voice Cloning Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Navigation")
    page = st.radio(
        "",
        ["🏠 Home", "👤 Characters", "🎬 Generate Audio", "📚 History", "⚙️ Settings"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Quick Stats")

    from utils.storage import load_characters, load_history
    chars = load_characters()
    hist = load_history()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(chars)}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(hist)}</div><div class="stat-label">Outputs</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="color:#4a5568;font-size:0.75rem;text-align:center;">Powered by XTTS v2 + Modal</p>', unsafe_allow_html=True)


# ── Page Routing ──────────────────────────────────────────────────────────────
if page == "🏠 Home":
    from pages import home
    home.render()
elif page == "👤 Characters":
    from pages import characters
    characters.render()
elif page == "🎬 Generate Audio":
    from pages import generate
    generate.render()
elif page == "📚 History":
    from pages import history
    history.render()
elif page == "⚙️ Settings":
    from pages import settings
    settings.render()