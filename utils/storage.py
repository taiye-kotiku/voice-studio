"""
Storage utilities — characters and generation history stored as JSON.
In production, swap for SQLite or Supabase.
"""

import json
import os
import shutil
import base64
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CHARS_FILE = DATA_DIR / "characters.json"
HIST_FILE = DATA_DIR / "history.json"
CHARS_DIR = DATA_DIR / "characters"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Ensure directories exist
for d in [DATA_DIR, CHARS_DIR, OUTPUTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Characters ────────────────────────────────────────────────────────────────

def load_characters() -> dict:
    if not CHARS_FILE.exists():
        return {}
    try:
        return json.loads(CHARS_FILE.read_text())
    except Exception:
        return {}


def save_character(name: str, language: str, description: str, wav_bytes: bytes, avatar_emoji: str = "🎤") -> str:
    """Save a new character and their voice sample."""
    chars = load_characters()
    char_id = f"char_{int(datetime.now().timestamp())}_{name.lower().replace(' ', '_')}"

    # Save voice WAV
    wav_path = CHARS_DIR / f"{char_id}.wav"
    wav_path.write_bytes(wav_bytes)

    chars[char_id] = {
        "id": char_id,
        "name": name,
        "language": language,
        "description": description,
        "avatar": avatar_emoji,
        "wav_path": str(wav_path),
        "sample_size_kb": round(len(wav_bytes) / 1024, 1),
        "created_at": datetime.now().isoformat(),
        "generations": 0,
    }
    CHARS_FILE.write_text(json.dumps(chars, indent=2))
    return char_id


def delete_character(char_id: str):
    chars = load_characters()
    if char_id in chars:
        wav_path = Path(chars[char_id]["wav_path"])
        if wav_path.exists():
            wav_path.unlink()
        del chars[char_id]
        CHARS_FILE.write_text(json.dumps(chars, indent=2))


def increment_generations(char_id: str):
    chars = load_characters()
    if char_id in chars:
        chars[char_id]["generations"] = chars[char_id].get("generations", 0) + 1
        CHARS_FILE.write_text(json.dumps(chars, indent=2))


def get_character_wav(char_id: str) -> bytes | None:
    chars = load_characters()
    if char_id not in chars:
        return None
    wav_path = Path(chars[char_id]["wav_path"])
    return wav_path.read_bytes() if wav_path.exists() else None


# ── History ───────────────────────────────────────────────────────────────────

def load_history() -> list:
    if not HIST_FILE.exists():
        return []
    try:
        return json.loads(HIST_FILE.read_text())
    except Exception:
        return []


def save_to_history(char_id: str, char_name: str, text: str, language: str, audio_bytes: bytes, duration_sec: float) -> str:
    """Save a generation result to history."""
    history = load_history()
    entry_id = f"gen_{int(datetime.now().timestamp())}"

    # Save audio file
    audio_path = OUTPUTS_DIR / f"{entry_id}.wav"
    audio_path.write_bytes(audio_bytes)

    entry = {
        "id": entry_id,
        "char_id": char_id,
        "char_name": char_name,
        "text": text,
        "language": language,
        "audio_path": str(audio_path),
        "audio_size_kb": round(len(audio_bytes) / 1024, 1),
        "duration_sec": round(duration_sec, 1),
        "created_at": datetime.now().isoformat(),
    }
    history.insert(0, entry)  # newest first
    HIST_FILE.write_text(json.dumps(history[:200], indent=2))  # keep last 200
    return entry_id


def get_audio_bytes(entry_id: str) -> bytes | None:
    history = load_history()
    for e in history:
        if e["id"] == entry_id:
            p = Path(e["audio_path"])
            return p.read_bytes() if p.exists() else None
    return None


def delete_history_entry(entry_id: str):
    history = load_history()
    for e in history:
        if e["id"] == entry_id:
            p = Path(e["audio_path"])
            if p.exists():
                p.unlink()
            break
    history = [e for e in history if e["id"] != entry_id]
    HIST_FILE.write_text(json.dumps(history, indent=2))


# ── Settings ──────────────────────────────────────────────────────────────────

SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "modal_workspace": "",
    "default_language": "en",
    "gpu_type": "A10G",
    "container_idle_timeout": 120,
    "theme": "dark",
}


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        saved = json.loads(SETTINGS_FILE.read_text())
        return {**DEFAULT_SETTINGS, **saved}
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))