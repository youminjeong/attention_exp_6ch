# =============================================
# audio.py
# =============================================
import numpy as np
import sounddevice as sd
import random
from config import DEVICE_REALTEK, DEVICE_UMC, SAMPLERATE, STIM_FREQ, VOLUME_DB_BASE, VOLUME_DB_RANGE, SPEAKER_CHANNELS, POSITIONS

def db_to_amplitude(db):
    """Convert dB to amplitude (0.0–1.0)"""
    return 10 ** (db / 20)

def make_tone(freq=STIM_FREQ, duration=0.5):
    """
    Generate stimulus tone
    - Base volume: VOLUME_DB_BASE (mean 66 dB)
    - Random variation of ±VOLUME_DB_RANGE (2 dB) on each call
    """
    db = VOLUME_DB_BASE + random.uniform(-VOLUME_DB_RANGE, VOLUME_DB_RANGE)
    volume = db_to_amplitude(db)

    t = np.linspace(0, duration, int(SAMPLERATE * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * volume
    return np.clip(wave, -1.0, 1.0).astype(np.float32)

def play_speaker(position, duration=0.5):
    device, n_ch, col = SPEAKER_CHANNELS[position]  
    tone = make_tone(duration=duration)
    buf = np.zeros((len(tone), n_ch), dtype=np.float32)
    buf[:, col] = tone
    sd.play(buf, samplerate=SAMPLERATE, device=device)
    sd.wait()

def test_all_speakers():
    """Play test tone from each speaker"""
    import time
    for pos in POSITIONS:
        print(f'  Testing: {pos}')
        play_speaker(pos)
        time.sleep(0.3)

def list_devices():
    print(sd.query_devices())
