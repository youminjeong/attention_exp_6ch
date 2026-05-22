import sounddevice as sd

print("=== 全体装置記録 ===")
print(sd.query_devices())

print("\n=== UMC404HD関連の装置を全部表示 ===")
devices = sd.query_devices()
for i, dev in enumerate(devices):
    if 'UMC' in dev['name'] or 'ASIO' in dev['name']:
        print(f"\n--- 装置 {i}番 ---")
        print(dev)