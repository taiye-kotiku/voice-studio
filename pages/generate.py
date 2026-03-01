"""Generate Audio page — the main production studio."""

import streamlit as st
import time
from datetime import datetime
from utils.storage import (
    load_characters, load_settings, save_to_history,
    increment_generations, get_character_wav
)
from utils.inference import (
    SUPPORTED_LANGUAGES, generate_audio_modal,
    generate_audio_http, generate_audio_demo
)

WORD_PER_MINUTE = 150  # avg speaking speed estimate


def estimate_duration(text: str) -> float:
    words = len(text.split())
    return round((words / WORD_PER_MINUTE) * 60, 1)


def render():
    st.markdown('<h2 style="font-weight:800;">🎬 Generate Audio</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8892b0;">Select a character, write your script, generate your voiceover.</p>', unsafe_allow_html=True)

    chars = load_characters()
    settings = load_settings()

    if not chars:
        st.warning("⚠️ No characters yet. Go to **👤 Characters** to create your first voice.")
        return

    # ── Layout ─────────────────────────────────────────────────────────────────
    left, right = st.columns([1, 1.2])

    # ── LEFT: Character + Settings ─────────────────────────────────────────────
    with left:
        st.markdown('<div class="section-header">1. Choose Character</div>', unsafe_allow_html=True)

        # Pre-select if coming from Characters page
        preselected_id = st.session_state.get("selected_char_id", None)
        char_names = {v["name"]: k for k, v in chars.items()}

        default_idx = 0
        if preselected_id:
            ids = list(chars.keys())
            if preselected_id in ids:
                default_idx = ids.index(preselected_id)

        selected_name = st.selectbox(
            "Character",
            list(char_names.keys()),
            index=default_idx,
            label_visibility="collapsed",
        )
        selected_char_id = char_names[selected_name]
        selected_char = chars[selected_char_id]

        # Character preview card
        char_lang = SUPPORTED_LANGUAGES.get(selected_char["language"], selected_char["language"])
        st.markdown(f"""
        <div class="voice-card selected">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="font-size:3rem;">{selected_char['avatar']}</div>
                <div>
                    <div style="font-weight:700;font-size:1.1rem;color:#e2e8f0;">{selected_char['name']}</div>
                    <div style="color:#8892b0;font-size:0.85rem;">{selected_char.get('description','')}</div>
                    <div style="margin-top:6px;">
                        <span class="tag lang">{char_lang}</span>
                        <span class="tag">📊 {selected_char.get('generations', 0)} uses</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Play voice sample
        wav_bytes = get_character_wav(selected_char_id)
        if wav_bytes:
            with st.expander("🎵 Preview voice sample"):
                st.audio(wav_bytes, format="audio/wav")

        st.markdown('<div class="section-header">2. Generation Settings</div>', unsafe_allow_html=True)

        # Language (can override character default)
        lang_options = list(SUPPORTED_LANGUAGES.values())
        default_lang_display = SUPPORTED_LANGUAGES.get(selected_char["language"], "🇺🇸 English")
        lang_idx = lang_options.index(default_lang_display) if default_lang_display in lang_options else 0

        lang_display = st.selectbox("Language", lang_options, index=lang_idx)
        lang_code = {v: k for k, v in SUPPORTED_LANGUAGES.items()}[lang_display]

        # Demo mode toggle
        demo_mode = st.toggle(
            "🧪 Demo Mode (no Modal needed)",
            value=not bool(settings.get("modal_workspace")),
            help="Enable to test the UI without deploying Modal. Generates a tone instead of real voice.",
        )

    # ── RIGHT: Script + Output ─────────────────────────────────────────────────
    with right:
        st.markdown('<div class="section-header">3. Write Your Script</div>', unsafe_allow_html=True)

        # Quick templates
        st.markdown("**Quick Templates:**")
        template_cols = st.columns(4)
        templates = {
            "Upwork Intro": "Hi, I'm Taiye. I'm an AI automation specialist with expertise in voice agents, n8n workflows, and end-to-end automation systems. Let's build something powerful together.",
            "Client Demo": "Here's a quick demo of the AI system I've built for your business. The voice agent can handle customer inquiries, book appointments, and escalate complex issues automatically.",
            "Video Outro": "If this video helped you, please like and subscribe. Drop your questions in the comments below, and I'll see you in the next one.",
            "UGC Hook": "Stop paying for overpriced voice APIs. I'll show you how to clone your voice for under a dollar per hour using open-source AI tools.",
        }
        for i, (label, text) in enumerate(templates.items()):
            with template_cols[i]:
                if st.button(label, key=f"tpl_{i}", use_container_width=True):
                    st.session_state["script_text"] = text

        # Script input
        script_key = "script_text"
        if script_key not in st.session_state:
            st.session_state[script_key] = ""

        # Check if quick generate was passed from home
        if "quick_generate" in st.session_state:
            qg = st.session_state.pop("quick_generate")
            if qg.get("text"):
                st.session_state[script_key] = qg["text"]

        script = st.text_area(
            "Script",
            value=st.session_state[script_key],
            height=200,
            placeholder="Write your script here. Be natural — XTTS v2 handles punctuation and pacing well.",
            label_visibility="collapsed",
            key="script_input",
        )

        # Character counter
        word_count = len(script.split()) if script.strip() else 0
        char_count = len(script)
        est_dur = estimate_duration(script) if script.strip() else 0

        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.markdown(f'<span class="tag">📝 {word_count} words</span>', unsafe_allow_html=True)
        with meta_col2:
            st.markdown(f'<span class="tag">🔤 {char_count} chars</span>', unsafe_allow_html=True)
        with meta_col3:
            st.markdown(f'<span class="tag">⏱️ ~{est_dur}s output</span>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Generate button
        generate_disabled = not script.strip()
        generate_clicked = st.button(
            "🚀 Generate Audio" if not demo_mode else "🧪 Generate (Demo Mode)",
            type="primary",
            use_container_width=True,
            disabled=generate_disabled,
        )

        if generate_disabled:
            st.caption("⬆️ Enter a script above to enable generation.")

        # ── Generation ─────────────────────────────────────────────────────────
        if generate_clicked and script.strip():
            progress_bar = st.progress(0)
            status = st.empty()

            try:
                status.markdown("⏳ **Connecting to Modal GPU...**")
                progress_bar.progress(15)

                speaker_bytes = get_character_wav(selected_char_id)
                if not speaker_bytes and not demo_mode:
                    st.error("Could not load voice sample for this character.")
                    return
                assert speaker_bytes is not None  # Pylance: guaranteed by guard above

                status.markdown("🎙️ **Cloning voice & synthesizing...**")
                progress_bar.progress(40)

                start_time = time.time()

                if demo_mode:
                    time.sleep(1.5)  # Simulate processing
                    audio_bytes, duration = generate_audio_demo(script, lang_code)
                else:
                    audio_bytes, duration = generate_audio_modal(script, speaker_bytes, lang_code)

                elapsed = round(time.time() - start_time, 1)

                status.markdown("💾 **Saving to history...**")
                progress_bar.progress(85)

                entry_id = save_to_history(
                    char_id=selected_char_id,
                    char_name=selected_char["name"],
                    text=script,
                    language=lang_code,
                    audio_bytes=audio_bytes,
                    duration_sec=duration,
                )
                increment_generations(selected_char_id)

                progress_bar.progress(100)
                status.empty()
                progress_bar.empty()

                # ── Result Display ──────────────────────────────────────────────
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1a2e1a,#162216);border:1px solid #2d5a2d;
                            border-radius:16px;padding:20px;margin:12px 0;">
                    <div style="color:#68d391;font-weight:700;font-size:1.1rem;margin-bottom:8px;">✅ Audio Generated!</div>
                    <div style="display:flex;gap:16px;flex-wrap:wrap;">
                        <span class="tag">⏱️ {duration}s audio</span>
                        <span class="tag">🚀 {elapsed}s render time</span>
                        <span class="tag">📁 {round(len(audio_bytes)/1024,1)} KB</span>
                        <span class="tag lang">{lang_display}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Audio player
                st.audio(audio_bytes, format="audio/wav")

                # Download
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{selected_char['name'].replace(' ', '_')}_{timestamp}.wav"
                st.download_button(
                    label="⬇️ Download WAV",
                    data=audio_bytes,
                    file_name=filename,
                    mime="audio/wav",
                    use_container_width=True,
                )

                if demo_mode:
                    st.info("🧪 This was demo mode. Deploy Modal and disable demo mode for real voice cloning.")

            except Exception as e:
                progress_bar.empty()
                status.empty()
                st.error(f"❌ Generation failed: {str(e)}")
                if "modal" in str(e).lower() or "connection" in str(e).lower():
                    st.info("💡 Is Modal deployed? Run `modal deploy modal_xtts.py` or enable Demo Mode.")