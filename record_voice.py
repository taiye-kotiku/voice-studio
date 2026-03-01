"""
🎙️ VoiceStudio — Voice Recorder
Records a clean voice sample for character creation.
Run: python record_voice.py

Uses sounddevice (works on Python 3.14+, no build tools needed)
Install: pip install sounddevice scipy
"""

import wave
import struct
import sys
import os
import time
import threading
from datetime import datetime

# ── Check dependencies ────────────────────────────────────────────────────────
try:
    import sounddevice as sd
    import numpy as np
    from scipy.io.wavfile import write as wav_write
except ImportError:
    print("\n❌ Missing dependencies. Run:")
    print("   pip install sounddevice scipy numpy")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
SAMPLE_RATE   = 24000   # XTTS v2 native sample rate
CHANNELS      = 1       # Mono
MIN_SECONDS   = 10
MAX_SECONDS   = 30
OUTPUT_DIR    = "voice_samples"

# ── Sample scripts to read aloud ─────────────────────────────────────────────
SAMPLE_SCRIPTS = [
    "Hi, my name is Taiye. I'm an AI automation specialist. I help businesses build voice agents, workflow automation, and AI-powered systems that save time and money.",
    "Welcome! I specialize in building intelligent automation systems using cutting-edge AI technology. From voice agents to complete workflow pipelines, I've got you covered.",
    "Good day. I build AI voice agents, n8n automation workflows, and WhatsApp bots for businesses around the world. Let me show you what's possible with modern AI.",
]


def clear_line():
    print("\r" + " " * 60 + "\r", end="", flush=True)


def record_voice(output_path: str, duration: int = 20) -> str:
    """Record audio from microphone and save as WAV."""

    # Check microphone is available
    try:
        device_info = sd.query_devices(kind="input")
        print(f"   🎤 Microphone: {device_info['name']}")
    except Exception:
        print("❌ No microphone found. Check your audio settings.")
        sys.exit(1)

    stop_flag = threading.Event()
    recorded_chunks = []

    print(f"\n{'─'*50}")
    print("  🔴 RECORDING — speak naturally and clearly")
    print(f"  ⏱️  Recording up to {duration} seconds")
    print("  ⏹️  Press ENTER to stop early")
    print(f"{'─'*50}\n")

    # Thread to listen for Enter key to stop early
    def wait_for_enter():
        input()
        stop_flag.set()

    enter_thread = threading.Thread(target=wait_for_enter, daemon=True)
    enter_thread.start()

    # Record in a blocking call with progress display
    start = time.time()

    def audio_callback(indata, frames, time_info, status):
        recorded_chunks.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=audio_callback,
    ):
        while not stop_flag.is_set():
            elapsed = time.time() - start
            if elapsed >= duration:
                break
            filled = int((elapsed / duration) * 30)
            bar = "█" * filled + "░" * (30 - filled)
            print(f"\r  [{bar}] {elapsed:.1f}s / {duration}s  ", end="", flush=True)
            time.sleep(0.1)

    elapsed_total = time.time() - start
    clear_line()
    print(f"  ✅ Recorded {elapsed_total:.1f} seconds\n")

    # Combine chunks and save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audio_data = np.concatenate(recorded_chunks, axis=0)
    wav_write(output_path, SAMPLE_RATE, audio_data)

    size_kb = round(os.path.getsize(output_path) / 1024, 1)
    print(f"  💾 Saved → {output_path}  ({size_kb} KB)")
    return output_path


def check_audio_quality(wav_path: str) -> dict:
    """Basic quality check on the recorded WAV."""
    with wave.open(wav_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        duration = wf.getnframes() / wf.getframerate()
        samples = struct.unpack(f"{len(frames)//2}h", frames)

    max_amplitude = max(abs(s) for s in samples)
    avg_amplitude = sum(abs(s) for s in samples) / len(samples)
    volume_pct = round((max_amplitude / 32767) * 100, 1)

    return {
        "duration": round(duration, 1),
        "volume_pct": volume_pct,
        "avg_amplitude": round(avg_amplitude, 1),
        "too_short": duration < MIN_SECONDS,
        "too_quiet": volume_pct < 20,
        "clipping": volume_pct > 98,
    }


def print_quality_report(quality: dict):
    print(f"\n{'─'*50}")
    print("  📊 RECORDING QUALITY REPORT")
    print(f"{'─'*50}")
    print(f"  ⏱️  Duration:  {quality['duration']}s", end="")
    if quality["too_short"]:
        print(f"  ⚠️  (minimum {MIN_SECONDS}s recommended)")
    else:
        print("  ✅")

    print(f"  🔊 Volume:    {quality['volume_pct']}%", end="")
    if quality["too_quiet"]:
        print("  ⚠️  (too quiet — speak louder or move mic closer)")
    elif quality["clipping"]:
        print("  ⚠️  (clipping — speak softer or move mic back)")
    else:
        print("  ✅")

    print(f"{'─'*50}\n")

    if quality["too_short"] or quality["too_quiet"] or quality["clipping"]:
        return False
    return True


def main():
    print("\n" + "═"*50)
    print("  🎙️  VoiceStudio — Voice Sample Recorder")
    print("═"*50)

    print("\n📋 WHAT MAKES A GOOD VOICE SAMPLE:")
    print("   • Speak for 10–30 seconds")
    print("   • Clear, natural pace — don't rush")
    print("   • Quiet room — no background noise or music")
    print("   • Normal conversational tone")
    print("   • Hold mic/headset 10–15cm from mouth")

    print("\n📝 READ THIS SCRIPT ALOUD WHEN RECORDING:\n")
    import random
    script = random.choice(SAMPLE_SCRIPTS)
    print(f'   "{script}"\n')
    print("   (You can say anything — this is just a suggestion)")

    # Choose duration
    print("\n⏱️  RECORDING DURATION:")
    print("   1. 15 seconds (quick)")
    print("   2. 20 seconds (recommended)")
    print("   3. 30 seconds (best quality)")
    choice = input("\n   Choose [1/2/3] (default: 2): ").strip() or "2"
    duration = {"1": 15, "2": 20, "3": 30}.get(choice, 20)

    # Output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"voice_sample_{timestamp}.wav"
    name = input(f"\n   Output filename [{default_name}]: ").strip() or default_name
    if not name.endswith(".wav"):
        name += ".wav"
    output_path = os.path.join(OUTPUT_DIR, name)

    # Countdown
    print("\n🎬 GET READY...")
    for i in range(3, 0, -1):
        print(f"   {i}...", flush=True)
        time.sleep(1)
    print("   GO!\n")

    # Record
    record_voice(output_path, duration)

    # Quality check
    quality = check_quality = check_audio_quality(output_path)
    passed = print_quality_report(quality)

    if passed:
        print("  🎉 Great recording! Upload this file to VoiceStudio:")
        print(f"     {os.path.abspath(output_path)}\n")
        print("  📋 NEXT STEPS:")
        print("     1. Open VoiceStudio → 👤 Characters")
        print("     2. Click 'Create New Character'")
        print(f"     3. Upload: {name}")
        print("     4. Give it a name (e.g. 'Taiye English')")
        print("     5. Hit Save — done!\n")
    else:
        print("  🔄 Try recording again for better results.")
        retry = input("  Record again? [Y/n]: ").strip().lower()
        if retry != "n":
            main()


if __name__ == "__main__":
    main()