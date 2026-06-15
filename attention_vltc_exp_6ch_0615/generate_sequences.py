
# =============================================
# generate_sequences.py
# Run once before the experiment
# Generates 30 stimulus sequences: 6 dual-task conditions × 5 trials
# =============================================
import random
import json
from config import POSITIONS, N_STIMULI, N_TRIALS, N_BACK_LEVELS, VLTC_CONDS, SEQ_FILE

def generate_sequence(n, n_stimuli=N_STIMULI, target_rate=0.3, min_match=1):
    """
    Generate a stimulus position sequence with n-back structure
    - First n positions: fully random
    - Thereafter: match with probability target_rate, otherwise non-match
    - Regenerates until at least min_match matches are included
    """
    while True:
        seq = [random.choice(POSITIONS) for _ in range(n)]

        for i in range(n, n_stimuli):
            if random.random() < target_rate:
                seq.append(seq[i - n])             # match
            else:
                others = [p for p in POSITIONS if p != seq[i - n]]
                seq.append(random.choice(others))  # non-match

        matches = sum(1 for i in range(n, n_stimuli) if seq[i] == seq[i - n])
        if matches >= min_match:
            return seq

def main():
    sequences = {}

    for vltc in VLTC_CONDS:
        for n in N_BACK_LEVELS:
            for t in range(1, N_TRIALS + 1):
                key = f'{vltc}_{n}back_trial{t}'
                sequences[key] = generate_sequence(n)

    with open(SEQ_FILE, 'w', encoding='utf-8') as f:
        json.dump(sequences, f, ensure_ascii=False, indent=2)

    print(f'{len(sequences)} sequences saved to {SEQ_FILE}.')
    for k, v in sequences.items():
        matches = sum(1 for i in range(n, N_STIMULI) if v[i] == v[i - n])
        print(f'  {k}: {v}  (matches: {matches})')

if __name__ == '__main__':
    main()