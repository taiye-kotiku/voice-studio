# 🎙️ VoiceStudio — Self-Hosted Voice Cloning Dashboard

Self-hosted voice cloning powered by **Coqui XTTS v2** + **Modal serverless GPU** + **Streamlit**.
Clone your voice once as a named **Character**, then generate unlimited voiceovers on demand — no per-character API fees.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Dashboard | Streamlit |
| Voice Model | Coqui XTTS v2 (multilingual) |
| GPU Compute | Modal (serverless, pay per use) |
| Storage | JSON files (local) |
| Hosting | Streamlit Cloud |

---

## Project Structure

```
voice_studio/
├── app.py                        ← Streamlit entry point — run this
├── modal_xtts.py                 ← Modal GPU backend — deploy this separately
├── client.py                     ← Python client for direct Modal calls + batch mode
├── requirements.txt              ← Python dependencies
├── Procfile                      ← Start command for Railway / Render
│
├── .streamlit/
│   ├── config.toml               ← Dark theme + server settings
│   └── secrets.toml.example      ← Template for Modal credentials (never commit the real one)
│
├── pages/
│   ├── __init__.py
│   ├── home.py                   ← Dashboard overview + quick stats
│   ├── characters.py             ← Create & manage voice characters
│   ├── generate.py               ← Main audio generation studio
│   ├── history.py                ← Browse, replay & download past generations
│   └── settings.py               ← Modal config, GPU type, connection test
│
├── utils/
│   ├── __init__.py
│   ├── storage.py                ← JSON persistence — characters, history, settings
│   └── inference.py              ← Modal SDK + HTTP client + demo mode
│
└── data/                         ← Auto-created on first run
    ├── characters.json           ← Character registry
    ├── history.json              ← Generation log (last 200 entries)
    ├── settings.json             ← User preferences
    ├── characters/               ← Voice sample WAV files (one per character)
    └── outputs/                  ← Generated audio WAV files
```

---

## Quick Start (Local)

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Deploy the Modal backend (one-time)
```bash
pip install modal
modal setup                    # Opens browser to authenticate
modal deploy modal_xtts.py     # Deploys GPU function to Modal cloud
```

### 3 — Run the dashboard
```bash
streamlit run app.py
```
Opens at **http://localhost:8501**

---

## Workflow

1. **👤 Characters** → Upload a 10–30s voice sample → Give it a name → Save
2. **🎬 Generate Audio** → Pick your character → Write script → Hit Generate
3. **📚 History** → Browse all past generations → Replay, download, or delete

---

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub (private recommended)
2. Go to **share.streamlit.io** → New app → select this repo → `app.py`
3. **Advanced settings → Secrets** → paste:

```toml
MODAL_TOKEN_ID     = "ak-xxxxxxxxxxxxxxxxxxxx"
MODAL_TOKEN_SECRET = "as-xxxxxxxxxxxxxxxxxxxx"
MODAL_WORKSPACE    = "your-modal-username"
```

4. Click **Deploy** → live at `https://your-app-name.streamlit.app`

---

## Demo Mode

Modal not deployed yet? Toggle **Demo Mode** on the Generate page to test the full UI — it generates a placeholder tone instead of real voice. Disable it once Modal is live.

---

## Supported Languages

`en` `it` `de` `es` `fr` `pt` `pl` `tr` `ru` `nl` `cs` `ar` `zh-cn` `ja` `hu` `ko`

---

## Cost vs ElevenLabs

| | VoiceStudio (Modal A10G) | ElevenLabs |
|--|--------------------------|------------|
| Per minute of audio | ~$0.003–0.006 | ~$0.18–0.60 per 1k chars |
| 100 voiceovers/mo | ~$0.30–$0.60 | $5–$22/mo subscription |
| Voice clones | Unlimited | Plan-limited |
| Self-hosted | ✅ | ❌ |

**VoiceStudio is 10–50x cheaper at scale.**

---

## Upgrade Path

| Feature | Current | When You Need It |
|---------|---------|-----------------|
| Storage | JSON files | Add Supabase for persistent cloud storage |
| Auth | None | Add Streamlit-Authenticator for multi-user |
| Hosting | Streamlit Cloud (free) | Move to Railway for always-on + custom domain |