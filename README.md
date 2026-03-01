# 🎙️ VoiceForge — Production Voice Cloning Dashboard

Self-hosted, GPU-powered voice cloning with a full management UI.
Built on Coqui XTTS v2 + Modal serverless GPU.

---

## Architecture

```
┌─────────────────────────────┐     ┌──────────────────────────────────┐
│   React Dashboard (claude.ai│────▶│  Modal FastAPI (voiceforge-api)  │
│   or your own hosting)      │     │  A10G GPU · XTTS v2              │
└─────────────────────────────┘     └──────────┬───────────────────────┘
                                               │
                               ┌───────────────┴─────────────────┐
                               │ voiceforge-models (Volume)       │
                               │ XTTS v2 weights (~2GB, cached)  │
                               ├─────────────────────────────────┤
                               │ voiceforge-storage (Volume)      │
                               │ /characters/ — voice samples     │
                               │ /audio/      — generated WAVs    │
                               │ /jobs/       — job records       │
                               └─────────────────────────────────┘
```

---

## Deploy Backend (5 minutes)

```bash
# 1. Install Modal
pip install modal
modal setup

# 2. Deploy
cd backend/
modal deploy modal_app.py

# 3. Copy your endpoint URL from the output, looks like:
#    https://YOUR-WORKSPACE--voiceforge-api.modal.run
```

---

## Use the Dashboard

### Option A — Paste into Claude.ai (fastest)
1. Open Claude.ai → New conversation
2. Upload `frontend/App.jsx`
3. Ask: "Run this React component"
4. Click ⚙ API → paste your Modal endpoint → CONNECT

### Option B — Host it yourself (Vercel, Netlify, etc.)
```bash
cd frontend/
npx create-react-app voiceforge --template minimal
# Replace src/App.js with App.jsx content
# Set API constant to your Modal URL
npm run build
# Deploy build/ to Vercel/Netlify
```

---

## Usage Flow

1. **Create a Character** (once per voice)
   - Go to CHARACTERS tab
   - Upload a clean WAV/MP3 sample (6–30 sec)
   - Give it a name, language, emoji
   - Character is saved permanently to Modal volume

2. **Generate Audio** (unlimited times)
   - Go to GENERATE tab
   - Select your character
   - Paste your script
   - Click ⚡ GENERATE
   - Play inline or download WAV

3. **History**
   - All jobs stored with metadata
   - Replay or re-download any past audio
   - Filter by character or job name

---

## REST API (for n8n / automation)

```bash
# List characters
GET /characters

# Create character
POST /characters
  multipart: name, description, language, avatar_emoji, speaker_wav (file)

# Generate audio
POST /generate
  form: char_id, text, job_name

# Download audio
GET /audio/{job_id}

# List jobs
GET /jobs?char_id=OPTIONAL
```

### n8n HTTP Request node — Generate Audio
```
Method: POST
URL: https://YOUR-WORKSPACE--voiceforge-api.modal.run/generate
Body Type: Form-Data
Fields:
  char_id: {{ $json.char_id }}
  text:    {{ $json.script }}
  job_name: {{ $json.job_name }}
```

---

## Cost (Modal A10G pricing)

| Action | Cost |
|--------|------|
| 30s voiceover | ~$0.003 |
| 2min voiceover | ~$0.012 |
| 100 voiceovers/month | ~$0.50–$2.00 |
| ElevenLabs equivalent | $22–$99/month |

**Savings: 95%+ vs ElevenLabs at scale.**

---

## Files

```
voiceforge/
├── backend/
│   └── modal_app.py     # Modal GPU inference + REST API + volume storage
└── frontend/
    └── App.jsx          # Full React dashboard (Characters + Generate + History)
```

---

## Tips

- **Cold start:** First call after idle takes 30–60s (container spins up). Subsequent calls in the same session are fast.
- **Best results:** 10–20 second voice sample, quiet room, natural speech
- **Batch:** Use the Python client's `batch_clone()` for parallel processing
- **Languages:** en, it, de, es, fr, pt, ru, ja, zh-cn, ko, ar, hu, pl, tr, nl