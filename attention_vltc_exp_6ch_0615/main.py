# =============================================
# main.py
# =============================================
import json
import csv
import os
import random
from datetime import datetime
from psychopy import core, event, visual, gui
from config import (CONDITIONS, N_TRIALS, N_RUNS, RESULT_DIR,
                    SEQ_FILE, STIM_DURATION, WAIT_DURATION, TRIAL_SEC)
from audio import play_speaker, test_all_speakers

# -----------------------------------------------
# Utilities
# -----------------------------------------------
def show_and_wait(win, msg, allowed=['space']):
    """Display message and wait for key press"""
    visual.TextStim(win, text=msg, color='white', height=0.06,
                    wrapWidth=1.8).draw()
    win.flip()
    event.waitKeys(keyList=allowed)

def load_sequences(path=SEQ_FILE):
    """Load pre-generated stimulus sequences from JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_order(participant_id, all_orders):
    """
    Save the condition order performed in each run to CSV
    all_orders: list of condition lists per run
    """
    os.makedirs(RESULT_DIR, exist_ok=True)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    fpath = os.path.join(RESULT_DIR, f'order_{participant_id}_{now}.csv')

    with open(fpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['participant_id', 'run', 'order', 'vltc', 'task', 'nback'])
        for run_num, orders in enumerate(all_orders, start=1):
            for order_idx, cond in enumerate(orders, start=1):
                writer.writerow([
                    participant_id,
                    run_num,
                    order_idx,
                    cond['vltc'],
                    cond['task'],
                    cond['nback'] if cond['nback'] else 'None'
                ])

    print(f'Condition order saved: {fpath}')

# -----------------------------------------------
# Trial execution
# -----------------------------------------------
def run_single_trial(win):
    """
    Single-task trial
    - No speaker stimulus
    - Wait for TRIAL_SEC (32 s) for COP measurement
    - Display remaining time every second
    """
    for elapsed in range(int(TRIAL_SEC)):
        remaining = int(TRIAL_SEC) - elapsed
        visual.TextStim(win, text=f'Maintain posture\n\nRemaining: {remaining} s',
                        color='white', height=0.07).draw()
        win.flip()
        if event.getKeys(keyList=['escape']):
            core.quit()
        core.wait(1.0)

def run_dual_trial(win, seq):
    """
    Dual-task trial
    - seq: list of 8 speaker positions
    - Each stimulus: 500 ms presentation -> 3500 ms interval
    - Participant responds verbally
    - Returns 'retry' if [R] pressed during ISI, else 'done'
    """
    for i, pos in enumerate(seq):
        # Display stimulus number + retry hint for experimenter
        visual.TextStim(win,
                        text=f'{i+1} / {len(seq)}\n\n[R] Retry',
                        color='gray', height=0.05).draw()
        win.flip()

        # Stimulus presentation (500 ms) — blocking, no retry during tone
        play_speaker(pos, duration=STIM_DURATION)

        # Inter-stimulus interval — poll for Escape or R
        t_start = core.getTime()
        while core.getTime() - t_start < WAIT_DURATION:
            keys = event.getKeys(keyList=['escape', 'r'])
            if 'escape' in keys:
                core.quit()
            if 'r' in keys:
                return 'retry'
            core.wait(0.01)

    return 'done'

# -----------------------------------------------
# Condition execution
# -----------------------------------------------
def run_condition(win, cond, trial_num, seqs):
    """
    Execute one trial of one condition (single or dual).
    For dual tasks, returns 'retry' if [R] pressed during ISI, else 'done'.
    """
    if cond['task'] == 'single':
        run_single_trial(win)
        return 'done'
    else:
        key = f"{cond['vltc']}_{cond['nback']}back_trial{trial_num}"
        seq = seqs[key]
        return run_dual_trial(win, seq)

def show_trial_complete(win):
    """
    Show 'Trial complete' screen after a dual task.
    [Space] -> proceed to next condition
    [R]     -> retry same trial
    Returns 'retry' or 'done'.
    """
    visual.TextStim(win,
                    text='Trial complete\n\n[Space]  Next  /  [R]  Retry',
                    color='white', height=0.07).draw()
    win.flip()
    while True:
        keys = event.waitKeys(keyList=['space', 'r', 'escape'])
        if 'escape' in keys:
            core.quit()
        if 'r' in keys:
            return 'retry'
        if 'space' in keys:
            return 'done'

# -----------------------------------------------
# Run execution
# -----------------------------------------------
def run_one_run(win, run_num, seqs, trial_counts):
    """
    Execute 8 conditions in randomized order.
    trial_counts: shared dict across all runs to track per-condition trial index
    Returns: list of conditions in the order they were performed
    """
    cond_order = CONDITIONS.copy()
    random.shuffle(cond_order)

    for order_idx, cond in enumerate(cond_order, start=1):
        task_label = 'Single task' if cond['task'] == 'single' \
                     else f'Dual task {cond["nback"]}-back'
        label = f"Run {run_num}  |  {order_idx}/{len(cond_order)}\n\n" \
                f"Condition: {cond['vltc']} / {task_label}\n\n" \
                f"Press [Space] when ready"
        show_and_wait(win, label)

        cond_key = f"{cond['vltc']}_{cond['task']}_{cond['nback']}"
        trial_counts[cond_key] = trial_counts.get(cond_key, 0) + 1
        trial_num = trial_counts[cond_key]

        while True:
            result = run_condition(win, cond, trial_num, seqs)

            if cond['task'] == 'single':
                # Single task: no retry, simple completion screen
                visual.TextStim(win, text='Trial complete',
                                color='white', height=0.07).draw()
                win.flip()
                core.wait(1.0)
                break

            # Dual task: mid-trial [R] pressed
            if result == 'retry':
                show_and_wait(win,
                              'Retrying this trial.\n\nPress [Space] when ready.',
                              allowed=['space'])
                continue

            # Dual task: trial finished normally -> show complete screen with retry option
            action = show_trial_complete(win)
            if action == 'retry':
                show_and_wait(win,
                              'Retrying this trial.\n\nPress [Space] when ready.',
                              allowed=['space'])
            else:
                break

    return cond_order

# -----------------------------------------------
# Practice session
# -----------------------------------------------
def run_practice(win):
    """
    Practice each n-back level with 4 stimuli
    Helps participants learn the task procedure
    """
    show_and_wait(win,
        'Practice Session\n\n'
        'When you hear a sound, say "はい" if the direction\n'
        'matches the one n steps ago, or "いいえ" if it does not.\n\n'
        'Press [Space] to start')

    from config import N_BACK_LEVELS, POSITIONS
    import random as rnd

    for n in N_BACK_LEVELS:
        show_and_wait(win, f'{n}-back practice\n\nPress [Space] to start')

        seq = [rnd.choice(POSITIONS) for _ in range(4)]

        for i, pos in enumerate(seq):
            visual.TextStim(win, text=f'Practice {i+1}/4',
                            color='gray', height=0.05).draw()
            win.flip()
            play_speaker(pos, duration=STIM_DURATION)
            t_start = core.getTime()
            while core.getTime() - t_start < WAIT_DURATION:
                if event.getKeys(keyList=['escape']):
                    core.quit()
                core.wait(0.01)

    show_and_wait(win, 'Practice complete!\n\nThe main experiment will now begin.\n\nPress [Space] to continue')

# -----------------------------------------------
# Main
# -----------------------------------------------
def main():
    # Participant ID via dialog
    dlg = gui.Dlg(title='VLTC Experiment')
    dlg.addField('Participant ID:')
    dlg.show()
    if not dlg.OK:
        core.quit()
    participant_id = dlg.data[0].strip()

    # Load stimulus sequences
    seqs = load_sequences()

    # PsychoPy window
    win = visual.Window(size=(1280, 720), fullscr=False,
                        color='black', units='norm')

    # Speaker test
    show_and_wait(win, 'Speaker test will now begin.\n\nPress [Space] to start')
    test_all_speakers()
    show_and_wait(win, 'Did you hear sounds from all 4 directions?\n\nPress [Space] to continue')

    # Practice
    run_practice(win)

    # Main experiment (5 runs)
    all_orders = []
    trial_counts = {}  # Shared across all runs: tracks per-condition trial index
    for run_num in range(1, N_RUNS + 1):
        show_and_wait(win, f'Run {run_num} / {N_RUNS}\n\nPress [Space] to start')

        cond_order = run_one_run(win, run_num, seqs, trial_counts)
        all_orders.append(cond_order)

        if run_num < N_RUNS:
            show_and_wait(win,
                f'Run {run_num} complete\n\n'
                f'Please rest for 3 minutes.\n\n'
                f'Press [Space] when ready')

    # Save condition order
    save_order(participant_id, all_orders)

    show_and_wait(win, 'Experiment complete!\nThank you.\n\nPress [Space] to exit')
    win.close()
    core.quit()

if __name__ == '__main__':
    main()