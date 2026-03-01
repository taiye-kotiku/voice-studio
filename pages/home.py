"""Home page — overview and quick actions."""

import streamlit as st
from datetime import datetime
from utils.storage import load_characters, load_history


def render():
    st.markdown('<h1 style="font-size:2.2rem;font-weight:800;">🎙️ VoiceStudio</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;font-size:1.05rem;margin-top:-12px;">Your self-hosted voice cloning workspace — powered by XTTS v2 + Modal</p>', unsafe_allow_html=True)

    st.markdown("---")

    chars = load_characters()
    history = load_history()

    # ── Stats Row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    total_chars = len(chars)
    total_gens = len(history)
    total_duration = sum(e.get("duration_sec", 0) for e in history)
    total_chars_text = sum(len(e.get("text", "")) for e in history)

    with c1:
        st.markdown(f'''<div class="stat-box">
            <div class="stat-number">{total_chars}</div>
            <div class="stat-label">Voice Characters</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="stat-box">
            <div class="stat-number">{total_gens}</div>
            <div class="stat-label">Generations</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        mins = round(total_duration / 60, 1)
        st.markdown(f'''<div class="stat-box">
            <div class="stat-number">{mins}m</div>
            <div class="stat-label">Audio Generated</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        est_cost = round(total_duration / 60 * 0.005, 3)
        st.markdown(f'''<div class="stat-box">
            <div class="stat-number">${est_cost}</div>
            <div class="stat-label">Est. GPU Cost</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Actions ──────────────────────────────────────────────────────────
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

        if not chars:
            st.markdown("""
            <div style="background:#1e2740;border:2px dashed #2d3561;border-radius:16px;padding:32px;text-align:center;">
                <div style="font-size:3rem;">👤</div>
                <h3 style="color:#e2e8f0;">No Characters Yet</h3>
                <p style="color:#8892b0;">Create your first voice character to get started.<br>
                Upload a 10–30 second audio sample and name it.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Create First Character", use_container_width=True):
                st.session_state.nav_target = "👤 Characters"
                st.rerun()
        else:
            # Quick generate form
            st.markdown('<div style="background:#1e2740;border-radius:16px;padding:20px;border:1px solid #2d3561;">', unsafe_allow_html=True)

            char_options = {v["name"]: k for k, v in chars.items()}
            char_names = list(char_options.keys())

            selected_name = st.selectbox("🎭 Character", char_names)
            quick_text = st.text_area(
                "📝 Script",
                placeholder="Type what you want your character to say...",
                height=120,
            )

            col_a, col_b = st.columns([2, 1])
            with col_a:
                if st.button("🚀 Generate Audio", use_container_width=True, type="primary"):
                    if quick_text.strip():
                        st.session_state["quick_generate"] = {
                            "char_id": char_options[selected_name],
                            "text": quick_text,
                        }
                        st.info("✅ Go to **Generate Audio** page to run!")
                    else:
                        st.warning("Please enter a script.")
            with col_b:
                if st.button("Full Studio →", use_container_width=True):
                    pass

            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">🕐 Recent Generations</div>', unsafe_allow_html=True)

        if not history:
            st.markdown('<p style="color:#8892b0;">No generations yet.</p>', unsafe_allow_html=True)
        else:
            for entry in history[:5]:
                created = datetime.fromisoformat(entry["created_at"]).strftime("%b %d, %H:%M")
                text_preview = entry["text"][:60] + "..." if len(entry["text"]) > 60 else entry["text"]
                char_name = entry.get("char_name", "Unknown")
                duration = entry.get("duration_sec", 0)

                st.markdown(f"""
                <div class="history-item">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#6c63ff;font-weight:600;font-size:0.85rem;">👤 {char_name}</span>
                        <span style="color:#4a5568;font-size:0.75rem;">{created}</span>
                    </div>
                    <div style="color:#cbd5e0;font-size:0.9rem;margin-top:6px;">"{text_preview}"</div>
                    <div style="color:#4a5568;font-size:0.75rem;margin-top:4px;">⏱️ {duration}s</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Getting Started Guide ──────────────────────────────────────────────────
    if not chars:
        st.markdown("---")
        st.markdown('<div class="section-header">🚀 Getting Started</div>', unsafe_allow_html=True)

        steps = [
            ("1", "Deploy Modal Backend", "Run `modal deploy modal_xtts.py` to spin up your GPU function on Modal's cloud."),
            ("2", "Create a Character", "Go to **Characters** → upload a 10–30 sec voice sample → name it → save."),
            ("3", "Generate Audio", "Go to **Generate Audio** → pick your character → type your script → hit Generate."),
            ("4", "Download & Use", "Download your WAV, plug it into your video editor, n8n pipeline, or content workflow."),
        ]

        cols = st.columns(4)
        for col, (num, title, desc) in zip(cols, steps):
            with col:
                st.markdown(f"""
                <div class="voice-card" style="text-align:center;">
                    <div style="font-size:2rem;font-weight:800;color:#6c63ff;">{num}</div>
                    <div style="font-weight:700;color:#e2e8f0;margin:8px 0;">{title}</div>
                    <div style="color:#8892b0;font-size:0.85rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)