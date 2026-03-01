"""Settings page — configure Modal connection and app preferences."""

import streamlit as st
from utils.storage import load_settings, save_settings
from utils.inference import SUPPORTED_LANGUAGES


def render():
    st.markdown('<h2 style="font-weight:800;">⚙️ Settings</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;">Configure your Modal backend and generation defaults.</p>', unsafe_allow_html=True)

    settings = load_settings()

    tab1, tab2, tab3 = st.tabs(["🖥️ Modal Backend", "🎛️ Generation Defaults", "📦 About"])

    # ── Modal Backend ────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">Modal Configuration</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#1e2740;border-radius:12px;padding:16px;border:1px solid #2d3561;margin-bottom:20px;">
            <p style="color:#8892b0;margin:0;font-size:0.9rem;">
            ℹ️ Deploy the backend first:<br>
            <code style="background:#0e1117;padding:4px 8px;border-radius:6px;color:#6c63ff;">pip install modal && modal setup && modal deploy modal_xtts.py</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        modal_workspace = st.text_input(
            "Modal Workspace Name",
            value=settings.get("modal_workspace", ""),
            placeholder="your-modal-username",
            help="Find this in your Modal dashboard URL"
        )

        http_endpoint = st.text_input(
            "HTTP Endpoint URL (optional)",
            value=settings.get("http_endpoint", ""),
            placeholder="https://your-workspace--xtts-api.modal.run",
            help="Use this for n8n or external callers"
        )

        gpu_options = ["A10G", "A100", "T4", "L4"]
        gpu_type = st.selectbox(
            "GPU Type",
            gpu_options,
            index=gpu_options.index(settings.get("gpu_type", "A10G")),
            help="A10G is the best cost/performance ratio for XTTS v2"
        )

        col1, col2 = st.columns(2)
        with col1:
            idle_timeout = st.number_input(
                "Container Idle Timeout (seconds)",
                min_value=30,
                max_value=600,
                value=settings.get("container_idle_timeout", 120),
                help="How long to keep container warm between calls. Higher = less cold starts, higher cost."
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#1a2e1a;border-radius:10px;padding:12px;border:1px solid #2d5a2d;">
                <div style="color:#68d391;font-size:0.85rem;">
                    💰 Est. keep-warm cost:<br>
                    <b>${round(idle_timeout/3600 * 1.10, 4)}/hr</b> idle<br>
                    <span style="color:#4a7c5a">({gpu_type} pricing)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-header">Connection Test</div>', unsafe_allow_html=True)

        col_test, col_status = st.columns([1, 2])
        with col_test:
            test_btn = st.button("🔌 Test Modal Connection", use_container_width=True)

        if test_btn:
            with st.spinner("Testing connection..."):
                try:
                    import modal
                    XTTSCloner = modal.Cls.from_name("xtts-voice-cloning", "XTTSCloner")
                    with col_status:
                        st.success("✅ Modal connection successful!")
                except ImportError:
                    with col_status:
                        st.error("❌ Modal not installed. Run: `pip install modal`")
                except Exception as e:
                    with col_status:
                        st.warning(f"⚠️ Could not connect: {str(e)[:80]}")
                        st.info("Make sure you've run `modal deploy modal_xtts.py`")

    # ── Generation Defaults ──────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Default Generation Settings</div>', unsafe_allow_html=True)

        lang_options = list(SUPPORTED_LANGUAGES.values())
        default_lang_display = SUPPORTED_LANGUAGES.get(settings.get("default_language", "en"), "🇺🇸 English")
        lang_idx = lang_options.index(default_lang_display) if default_lang_display in lang_options else 0

        default_lang_display = st.selectbox("Default Language", lang_options, index=lang_idx)
        default_lang = {v: k for k, v in SUPPORTED_LANGUAGES.items()}[default_lang_display]

    # ── About ────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">About VoiceStudio</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1e2740;border-radius:16px;padding:24px;border:1px solid #2d3561;">
            <h3 style="color:#e2e8f0;">🎙️ VoiceStudio</h3>
            <p style="color:#8892b0;">Self-hosted voice cloning dashboard powered by Coqui XTTS v2 and Modal serverless GPU compute.</p>
            
            <div style="margin:16px 0;">
                <div style="color:#e2e8f0;font-weight:600;margin-bottom:8px;">Tech Stack</div>
                <span class="tag">Coqui XTTS v2</span>
                <span class="tag">Modal GPU</span>
                <span class="tag">Streamlit</span>
                <span class="tag">Python 3.10+</span>
            </div>

            <div style="margin:16px 0;">
                <div style="color:#e2e8f0;font-weight:600;margin-bottom:8px;">Cost vs ElevenLabs</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                    <div style="background:#0e1117;border-radius:10px;padding:12px;border:1px solid #2d3561;">
                        <div style="color:#68d391;font-weight:700;">VoiceStudio (Modal)</div>
                        <div style="color:#a0aec0;font-size:0.85rem;">~$0.003–0.006/min audio</div>
                        <div style="color:#4a5568;font-size:0.8rem;">Pay per actual GPU use</div>
                    </div>
                    <div style="background:#0e1117;border-radius:10px;padding:12px;border:1px solid #2d3561;">
                        <div style="color:#fc8181;font-weight:700;">ElevenLabs</div>
                        <div style="color:#a0aec0;font-size:0.85rem;">$0.18–0.60/1k chars</div>
                        <div style="color:#4a5568;font-size:0.8rem;">Subscription required</div>
                    </div>
                </div>
            </div>

            <div style="color:#4a5568;font-size:0.8rem;margin-top:16px;">
                Supports 16 languages: EN, IT, DE, ES, FR, PT, PL, TR, RU, NL, CS, AR, ZH, JA, HU, KO
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Save Button ───────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("💾 Save Settings", type="primary"):
        updated = {
            **settings,
            "modal_workspace": modal_workspace,
            "http_endpoint": http_endpoint,
            "gpu_type": gpu_type,
            "container_idle_timeout": idle_timeout,
            "default_language": default_lang,
        }
        save_settings(updated)
        st.success("✅ Settings saved!")