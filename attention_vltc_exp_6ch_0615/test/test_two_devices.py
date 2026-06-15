# test_two_devices.py
import sounddevice as sd
import numpy as np
import threading

SAMPLERATE = 44100
duration = 2.0

t = np.linspace(0, duration, int(SAMPLERATE * duration))
tone = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

def play_umc(col):
    buf = np.zeros((len(tone), 4), dtype=np.float32)
    buf[:, col] = tone
    sd.play(buf, samplerate=SAMPLERATE, device=26)  # UMC404HD
    sd.wait()

def play_realtek(col):
    buf = np.zeros((len(tone), 8), dtype=np.float32)
    buf[:, col] = tone
    sd.play(buf, samplerate=SAMPLERATE, device=21)  # Realtek
    sd.wait()

t1 = threading.Thread(target=play_umc, args=(0,))
t2 = threading.Thread(target=play_realtek, args=(0,))

t1.start()
t2.start()
t1.join()
t2.join()