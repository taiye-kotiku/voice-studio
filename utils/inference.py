"""
Modal inference client — wraps the XTTS v2 Modal function call.
Handles both direct Modal SDK calls and HTTP endpoint fallback.
"""

import time
import io
import wave
from pathlib import Path


SUPPORTED_LANGUAGES = {
    "en": "🇺🇸 English",
    "it": "🇮🇹 Italian",
    "de": "🇩🇪 German",
    "es": "🇪🇸 Spanish",
    "fr": "🇫🇷 French",
    "pt": "🇧🇷 Portuguese",
    "pl": "🇵🇱 Polish",
    "tr": "🇹🇷 Turkish",
    "ru": "🇷🇺 Russian",
    "nl": "🇳🇱 Dutch",
    "cs": "🇨🇿 Czech",
    "ar": "🇸🇦 Arabic",
    "zh-cn": "🇨🇳 Chinese",
    "ja": "🇯🇵 Japanese",
    "hu": "🇭🇺 Hungarian",
    "ko": "🇰🇷 Korean",
}


def get_audio_duration(wav_bytes: bytes) -> float:
    """Get duration in seconds from WAV bytes."""
    try:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf) as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return 0.0


def generate_audio_modal(text: str, speaker_wav_bytes: bytes, language: str = "en") -> tuple[bytes, float]:
    """
    Call Modal XTTS function directly via Modal SDK.
    Returns (audio_bytes, duration_seconds)
    """
    import modal

    start = time.time()

    XTTSCloner = modal.Cls.from_name("xtts-voice-cloning", "XTTSCloner")
    cloner = XTTSCloner()
    audio_bytes = cloner.clone_voice.remote(text, speaker_wav_bytes, language)

    elapsed = time.time() - start
    duration = get_audio_duration(audio_bytes)

    return audio_bytes, duration


def generate_audio_http(text: str, speaker_wav_bytes: bytes, language: str, endpoint_url: str) -> tuple[bytes, float]:
    """
    Call via HTTP endpoint (for n8n or external callers).
    Returns (audio_bytes, duration_seconds)
    """
    import requests

    response = requests.post(
        endpoint_url,
        data={"text": text, "language": language},
        files={"speaker_wav": ("speaker.wav", speaker_wav_bytes, "audio/wav")},
        timeout=120,
    )
    response.raise_for_status()
    audio_bytes = response.content
    duration = get_audio_duration(audio_bytes)
    return audio_bytes, duration


def generate_audio_demo(text: str, language: str) -> tuple[bytes, float]:
    """
    Demo mode — generates silent WAV so the UI works without Modal deployed.
    Replace this with real Modal call in production.
    """
    import struct
    import math

    sample_rate = 24000
    # Generate 3 seconds of silence as a valid WAV
    num_samples = sample_rate * 3
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        # Write a simple tone so it's audible in demo
        for i in range(num_samples):
            val = int(3000 * math.sin(2 * math.pi * 440 * i / sample_rate))
            w.writeframes(struct.pack("<h", val))
    wav_buf.seek(0)
    audio_bytes = wav_buf.read()
    duration = get_audio_duration(audio_bytes)
    return audio_bytes, duration