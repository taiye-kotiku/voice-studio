"""
Self-Hosted Voice Cloning Pipeline
Coqui XTTS v2 deployed on Modal (serverless GPU)
"""

import modal
import io
from pathlib import Path

# ── Modal App Setup ──────────────────────────────────────────────────────────
app = modal.App("xtts-voice-cloning")

# Docker image with all deps pre-installed
xtts_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "libsndfile1")
    .pip_install(
        "TTS==0.22.0",          # Coqui TTS (includes XTTS v2)
        "torch==2.1.0",
        "torchaudio==2.1.0",
        "fastapi",
        "python-multipart",
        "pydub",
        "numpy",
        "scipy",
    )
)

# Persistent volume to cache the XTTS model weights (~2 GB)
model_volume = modal.Volume.from_name("xtts-model-cache", create_if_missing=True)
MODEL_DIR = "/model-cache"


# ── Core Inference Class ─────────────────────────────────────────────────────
@app.cls(
    gpu="A10G",                         # A10G = good balance of speed/cost
    image=xtts_image,
    volumes={MODEL_DIR: model_volume},
    timeout=300,
    container_idle_timeout=120,         # Keep warm for 2 min between calls
)
class XTTSCloner:

    @modal.enter()
    def load_model(self):
        """Load XTTS v2 once per container (cached in volume)."""
        from TTS.api import TTS
        import torch

        print("Loading XTTS v2 model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False,
        ).to(self.device)
        print(f"Model loaded on {self.device}")

    @modal.method()
    def clone_voice(
        self,
        text: str,
        speaker_wav_bytes: bytes,
        language: str = "en",
    ) -> bytes:
        """
        Clone voice and synthesize text.

        Args:
            text:               The script to synthesize
            speaker_wav_bytes:  Raw bytes of your voice sample WAV/MP3
            language:           Language code (en, it, de, es, fr, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko)

        Returns:
            WAV audio bytes of the generated voiceover
        """
        import tempfile
        import soundfile as sf
        import numpy as np

        # Write speaker sample to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as ref_f:
            ref_f.write(speaker_wav_bytes)
            ref_path = ref_f.name

        # Run XTTS inference
        wav = self.tts.tts(
            text=text,
            speaker_wav=ref_path,
            language=language,
        )

        # Convert to bytes
        buf = io.BytesIO()
        sf.write(buf, np.array(wav), samplerate=24000, format="WAV")
        buf.seek(0)
        return buf.read()


# ── FastAPI Web Endpoint (optional HTTP interface) ───────────────────────────
@app.function(
    image=xtts_image,
    gpu="A10G",
    volumes={MODEL_DIR: model_volume},
    timeout=300,
)
@modal.web_endpoint(method="POST", label="xtts-api")
async def synthesize_api(request):
    """
    HTTP endpoint — multipart form:
      - text:         string
      - language:     string (default: en)
      - speaker_wav:  file upload (WAV or MP3)
    Returns: audio/wav binary
    """
    from fastapi import UploadFile, Form, Response
    from fastapi.responses import Response as FastResponse

    form = await request.form()
    text = form.get("text", "")
    language = form.get("language", "en")
    speaker_file: UploadFile = form.get("speaker_wav")
    speaker_bytes = await speaker_file.read()

    cloner = XTTSCloner()
    audio_bytes = cloner.clone_voice.remote(text, speaker_bytes, language)

    return FastResponse(content=audio_bytes, media_type="audio/wav")