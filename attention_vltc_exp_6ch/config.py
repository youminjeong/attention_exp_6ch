# =============================================
# config.py
# =============================================

# --- オーディオデバイス番号---
DEVICE_UMC     = 6    # ← UMC404HDのデバイス番号に変更
DEVICE_REALTEK = 8    # ← Realtekのデバイス番号に変更

SAMPLERATE      = 44100
STIM_FREQ       = 1000   # 刺激音の周波数（Hz）
VOLUME_DB_BASE  = 66     # 基準音量（dB SPL）
VOLUME_DB_RANGE = 2      # ランダム変動範囲（±dB）

# --- 6方向スピーカーマッピング ---
# 構造: '方向名': (デバイス番号, 総チャンネル数, col番号)
#
# UMC404HD（4chモノ）:
#   col 0 = PLAYBACK端子1番
#   col 1 = PLAYBACK端子2番
#   col 2 = PLAYBACK端子3番
#   col 3 = PLAYBACK端子4番
#
# Realtek（2chステレオ）:
#   col 0 = L（フロントまたはリアの緑端子）
#   col 1 = R（フロントまたはリアの緑端子）

SPEAKER_CHANNELS = {
    '1':        (DEVICE_UMC,     4, 0),
    '2':        (DEVICE_UMC,     4, 1),
    '3':        (DEVICE_UMC,     4, 2),
    '4':        (DEVICE_UMC,     4, 3),
    '5':        (DEVICE_REALTEK, 2, 0),
    '6':        (DEVICE_REALTEK, 2, 1),
}
POSITIONS = list(SPEAKER_CHANNELS.keys())

# --- タイミング ---
STIM_DURATION = 0.5    # 刺激提示時間（秒）
WAIT_DURATION = 2.5    # 次の刺激までの待機時間（秒）
N_STIMULI     = 10     # 1試行あたりの刺激数
TRIAL_SEC     = 30.0   # 1試行の総時間（= 3.0 × 10）

# --- 実験構造 ---
N_TRIALS      = 5
N_BACK_LEVELS = [1, 2, 3]
VLTC_CONDS    = ['NC', 'VLTC']
N_RUNS        = 5

# 条件リスト（8条件）
CONDITIONS = []
for v in VLTC_CONDS:
    CONDITIONS.append({'vltc': v, 'task': 'single', 'nback': None})
for v in VLTC_CONDS:
    for n in N_BACK_LEVELS:
        CONDITIONS.append({'vltc': v, 'task': 'dual', 'nback': n})

# --- ファイル ---
SEQ_FILE   = 'sequences.json'
RESULT_DIR = 'results'