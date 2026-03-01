"""Characters page — create, manage, and preview voice characters."""

import streamlit as st
from datetime import datetime
from utils.storage import (
    load_characters, save_character, delete_character, get_character_wav
)
from utils.inference import SUPPORTED_LANGUAGES

AVATAR_OPTIONS = ["🎤", "🧑‍💼", "👩‍💼", "🧑‍🎨", "👩‍🎤", "🧑‍💻", "👨‍🏫", "👩‍🔬", "🎭", "🤖", "⭐", "🦁"]


def render():
    st.markdown('<h2 style="font-weight:800;">👤 Voice Characters</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;">Create reusable voice clones. Upload once, use forever.</p>', unsafe_allow_html=True)

    chars = load_characters()

    # ── Create New Character ───────────────────────────────────────────────────
    with st.expander("➕ Create New Character", expanded=not bool(chars)):
        st.markdown('<div class="section-header">New Voice Character</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 1])

        with col1:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                char_name = st.text_input("Character Name *", placeholder="e.g. My English Voice, Taiye Professional")
            with col_b:
                avatar = st.selectbox("Avatar", AVATAR_OPTIONS)

            char_desc = st.text_input("Description", placeholder="e.g. Deep professional tone for client demos")

            lang_options = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
            lang_display = st.selectbox(
                "Primary Language *",
                list(SUPPORTED_LANGUAGES.values()),
                index=0
            )
            selected_lang = lang_options[lang_display]

        with col2:
            st.markdown("**Voice Sample *")
            voice_file = st.file_uploader(
                "Upload WAV or MP3",
                type=["wav", "mp3", "m4a", "ogg"],
                label_visibility="collapsed",
            )
            if voice_file:
                st.audio(voice_file, format="audio/wav")
                size_kb = round(voice_file.size / 1024, 1)
                st.markdown(f'<span class="tag">📁 {size_kb} KB</span> <span class="tag lang">{lang_display}</span>', unsafe_allow_html=True)

            st.markdown("")
            st.markdown("""
            <div style="background:#0e1117;border-radius:10px;padding:12px;border:1px solid #1e2740;">
                <p style="color:#8892b0;font-size:0.8rem;margin:0;">
                💡 <b style="color:#a0aec0;">Tips for best quality:</b><br>
                • 10–30 seconds of clear speech<br>
                • No background music or noise<br>
                • Normal conversational pace<br>
                • WAV format preferred
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            save_clicked = st.button("💾 Save Character", type="primary", use_container_width=True)

        if save_clicked:
            if not char_name.strip():
                st.error("Please enter a character name.")
            elif not voice_file:
                st.error("Please upload a voice sample.")
            else:
                with st.spinner(f"Saving character '{char_name}'..."):
                    voice_bytes = voice_file.read()
                    char_id = save_character(
                        name=char_name.strip(),
                        language=selected_lang,
                        description=char_desc.strip(),
                        wav_bytes=voice_bytes,
                        avatar_emoji=avatar,
                    )
                st.success(f"✅ Character **{char_name}** created! (ID: `{char_id[:20]}...`)")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Character Gallery ──────────────────────────────────────────────────────
    if not chars:
        st.markdown("""
        <div style="text-align:center;padding:60px;background:#1e2740;border-radius:16px;border:2px dashed #2d3561;">
            <div style="font-size:4rem;">🎤</div>
            <h3 style="color:#e2e8f0;">No characters yet</h3>
            <p style="color:#8892b0;">Use the form above to create your first voice character.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div class="section-header">Your Characters ({len(chars)})</div>', unsafe_allow_html=True)

    # Grid of character cards
    char_list = list(chars.values())
    cols = st.columns(3)

    for idx, char in enumerate(char_list):
        col = cols[idx % 3]
        with col:
            created = datetime.fromisoformat(char["created_at"]).strftime("%b %d, %Y")
            lang_display = SUPPORTED_LANGUAGES.get(char["language"], char["language"])

            st.markdown(f"""
            <div class="voice-card">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                    <div style="font-size:2.5rem;">{char['avatar']}</div>
                    <div>
                        <div style="font-weight:700;font-size:1.05rem;color:#e2e8f0;">{char['name']}</div>
                        <div style="color:#8892b0;font-size:0.8rem;">{char.get('description','No description')}</div>
                    </div>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
                    <span class="tag lang">{lang_display}</span>
                    <span class="tag">📊 {char.get('generations', 0)} generations</span>
                    <span class="tag">🗓️ {created}</span>
                </div>
                <div style="color:#4a5568;font-size:0.75rem;">Sample: {char.get('sample_size_kb','?')} KB</div>
            </div>
            """, unsafe_allow_html=True)

            # Preview audio
            wav_bytes = get_character_wav(char["id"])
            if wav_bytes:
                st.audio(wav_bytes, format="audio/wav")

            # Actions
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎬 Use", key=f"use_{char['id']}", use_container_width=True):
                    st.session_state["selected_char_id"] = char["id"]
                    st.info("✅ Character selected! Go to **Generate Audio**.")
            with col_b:
                if st.button("🗑️ Delete", key=f"del_{char['id']}", use_container_width=True):
                    st.session_state[f"confirm_del_{char['id']}"] = True

            # Confirm delete
            if st.session_state.get(f"confirm_del_{char['id']}"):
                st.warning(f"Delete **{char['name']}**?")
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button("Yes, delete", key=f"yes_{char['id']}", use_container_width=True):
                        delete_character(char["id"])
                        st.session_state.pop(f"confirm_del_{char['id']}", None)
                        st.rerun()
                with col_n:
                    if st.button("Cancel", key=f"no_{char['id']}", use_container_width=True):
                        st.session_state.pop(f"confirm_del_{char['id']}", None)
                        st.rerun()