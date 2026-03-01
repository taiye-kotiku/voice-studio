"""History page — browse and replay all past generations."""

import streamlit as st
from datetime import datetime
from pathlib import Path
from utils.storage import load_history, load_characters, delete_history_entry
from utils.inference import SUPPORTED_LANGUAGES


def render():
    st.markdown('<h2 style="font-weight:800;">📚 Generation History</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;">All your past voiceover generations, ready to replay or download.</p>', unsafe_allow_html=True)

    history = load_history()
    chars = load_characters()

    if not history:
        st.markdown("""
        <div style="text-align:center;padding:60px;background:#1e2740;border-radius:16px;border:2px dashed #2d3561;">
            <div style="font-size:4rem;">📭</div>
            <h3 style="color:#e2e8f0;">No generations yet</h3>
            <p style="color:#8892b0;">Go to <b>Generate Audio</b> to create your first voiceover.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Filter Bar ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search scripts...", placeholder="Filter by text content...")
    with col2:
        char_filter_options = ["All Characters"] + [v["name"] for v in chars.values()]
        char_filter = st.selectbox("Character", char_filter_options)
    with col3:
        lang_filter_options = ["All Languages"] + list(SUPPORTED_LANGUAGES.values())
        lang_filter = st.selectbox("Language", lang_filter_options)

    # Apply filters
    filtered = history
    if search.strip():
        filtered = [e for e in filtered if search.lower() in e.get("text", "").lower()]
    if char_filter != "All Characters":
        filtered = [e for e in filtered if e.get("char_name") == char_filter]
    if lang_filter != "All Languages":
        lang_code = {v: k for k, v in SUPPORTED_LANGUAGES.items()}.get(lang_filter)
        if lang_code:
            filtered = [e for e in filtered if e.get("language") == lang_code]

    # ── Stats ───────────────────────────────────────────────────────────────────
    total_dur = sum(e.get("duration_sec", 0) for e in filtered)
    st.markdown(f"""
    <div style="display:flex;gap:16px;margin:12px 0 20px 0;">
        <span class="tag">📊 {len(filtered)} results</span>
        <span class="tag">⏱️ {round(total_dur/60,1)}m total audio</span>
        <span class="tag">💰 Est. ${round(total_dur/60*0.005,3)} GPU cost</span>
    </div>
    """, unsafe_allow_html=True)

    # ── History List ────────────────────────────────────────────────────────────
    for entry in filtered:
        entry_id = entry["id"]
        created = datetime.fromisoformat(entry["created_at"]).strftime("%b %d, %Y · %H:%M")
        char_name = entry.get("char_name", "Unknown")
        lang_display = SUPPORTED_LANGUAGES.get(entry.get("language", "en"), entry.get("language", "en"))
        text = entry.get("text", "")
        duration = entry.get("duration_sec", 0)

        # Find char avatar
        char_avatar = "🎤"
        for c in chars.values():
            if c["name"] == char_name:
                char_avatar = c.get("avatar", "🎤")
                break

        with st.container():
            col_info, col_audio, col_actions = st.columns([2.5, 2, 1])

            with col_info:
                st.markdown(f"""
                <div style="padding:4px 0;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="font-size:1.4rem;">{char_avatar}</span>
                        <div>
                            <span style="color:#6c63ff;font-weight:600;">{char_name}</span>
                            <span style="color:#4a5568;font-size:0.8rem;"> · {created}</span>
                        </div>
                    </div>
                    <div style="color:#cbd5e0;font-size:0.9rem;line-height:1.5;margin-bottom:8px;">
                        "{text[:120]}{"..." if len(text)>120 else ""}"
                    </div>
                    <div>
                        <span class="tag lang">{lang_display}</span>
                        <span class="tag">⏱️ {duration}s</span>
                        <span class="tag">📁 {entry.get('audio_size_kb','?')} KB</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_audio:
                audio_path = Path(entry.get("audio_path", ""))
                if audio_path.exists():
                    audio_bytes = audio_path.read_bytes()
                    st.audio(audio_bytes, format="audio/wav")
                else:
                    st.markdown('<span style="color:#4a5568;font-size:0.85rem;">⚠️ File not found</span>', unsafe_allow_html=True)

            with col_actions:
                if audio_path.exists():
                    audio_bytes = audio_path.read_bytes()
                    timestamp = datetime.fromisoformat(entry["created_at"]).strftime("%Y%m%d_%H%M")
                    fname = f"{char_name.replace(' ','_')}_{timestamp}.wav"
                    st.download_button(
                        "⬇️ Download",
                        data=audio_bytes,
                        file_name=fname,
                        mime="audio/wav",
                        use_container_width=True,
                        key=f"dl_{entry_id}",
                    )
                if st.button("🗑️ Delete", key=f"del_{entry_id}", use_container_width=True):
                    delete_history_entry(entry_id)
                    st.rerun()

            st.markdown("<hr style='border-color:#1e2740;margin:8px 0;'>", unsafe_allow_html=True)