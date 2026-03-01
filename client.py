"""
Voice Cloning Client
Call your Modal XTTS pipeline from Python or plug into n8n/automation.
"""

import modal
import sys
from pathlib import Path


def clone_voice(
    text: str,
    speaker_wav_path: str,
    output_path: str = "output.wav",
    language: str = "en",
):
    """
    Clone your voice and generate a voiceover.

    Args:
        text:             Script to synthesize
        speaker_wav_path: Path to your voice sample (WAV or MP3, 6–30 sec ideal)
        output_path:      Where to save the result
        language:         Language code (en, it, de, es, fr, etc.)
    """
    # Read voice sample
    speaker_bytes = Path(speaker_wav_path).read_bytes()

    # Call remote Modal function
    print(f"🎙️  Cloning voice | lang={language} | {len(text)} chars")
    XTTSCloner = modal.Cls.from_name("xtts-voice-cloning", "XTTSCloner")
    cloner = XTTSCloner()
    audio_bytes = cloner.clone_voice.remote(text, speaker_bytes, language)

    # Save output
    Path(output_path).write_bytes(audio_bytes)
    print(f"✅  Audio saved → {output_path}  ({len(audio_bytes)/1024:.1f} KB)")
    return output_path


# ── Batch Processing (for content pipelines) ────────────────────────────────
def batch_clone(jobs: list[dict], speaker_wav_path: str, language: str = "en"):
    """
    Process multiple scripts in parallel using Modal's .map()

    jobs = [
        {"text": "Script one...", "output": "intro.wav"},
        {"text": "Script two...", "output": "demo.wav"},
    ]
    """
    import modal

    speaker_bytes = Path(speaker_wav_path).read_bytes()
    XTTSCloner = modal.Cls.from_name("xtts-voice-cloning", "XTTSCloner")
    cloner = XTTSCloner()

    texts = [j["text"] for j in jobs]
    outputs = [j["output"] for j in jobs]

    # Parallel inference — Modal spins up multiple containers
    results = list(
        cloner.clone_voice.map(
            texts,
            [speaker_bytes] * len(texts),
            [language] * len(texts),
        )
    )

    for audio_bytes, out_path in zip(results, outputs):
        Path(out_path).write_bytes(audio_bytes)
        print(f"✅  {out_path}")

    return outputs


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="XTTS Voice Cloning Client")
    parser.add_argument("--text", required=True, help="Script to synthesize")
    parser.add_argument("--speaker", required=True, help="Path to voice sample WAV/MP3")
    parser.add_argument("--output", default="output.wav", help="Output WAV path")
    parser.add_argument("--language", default="en", help="Language code (en, it, de...)")
    args = parser.parse_args()

    clone_voice(args.text, args.speaker, args.output, args.language)