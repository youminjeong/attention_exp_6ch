# test_three_speakers.py
import sounddevice as sd
import numpy as np
import threading
import time

DEVICE_UMC     = 26   # UMC404HD
DEVICE_REALTEK = 21   # Realtek HD Audio output

SAMPLERATE = 44100
duration  = 2.0

t    = np.linspace(0, duration, int(SAMPLERATE * duration))
tone = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

# =====================
# 再生関数
# =====================
def play(device, n_ch, col):
    buf = np.zeros((len(tone), n_ch), dtype=np.float32)
    buf[:, col] = tone
    try:
        sd.play(buf, samplerate=SAMPLERATE, device=device)
        sd.wait()
    except Exception as e:
        print(f"  ❌ 장치{device} col{col} 실패: {e}")

# =====================
# テスト
# =====================

# テスト1: UMC404HD ch1
print("テスト1: UMC404HD speaker (ch1)")
play(DEVICE_UMC, 4, 0)
time.sleep(0.5)

# テスト2: Realtek 左
print("テスト2: Realtek speaker (L)")
play(DEVICE_REALTEK, 8, 0)
time.sleep(0.5)

# テスト3: Realtek 右
print("テスト3: Realtek speaker (R)")
play(DEVICE_REALTEK, 8, 1)
time.sleep(0.5)

# テスト4: 同時再生
print("テスト4: 同時再生")
t1 = threading.Thread(target=play, args=(DEVICE_UMC,     4, 0))
t2 = threading.Thread(target=play, args=(DEVICE_REALTEK, 8, 0))
t3 = threading.Thread(target=play, args=(DEVICE_REALTEK, 8, 1))
t1.start(); t2.start(); t3.start()
t1.join();  t2.join();  t3.join()