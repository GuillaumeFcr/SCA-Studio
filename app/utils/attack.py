import os
import threading
import numpy as np


def _run_attack_thread(
    board,
    runs_per_measure,
    out_directory,
    injector,
    trigger,
    stop_event,
):
    """Acquisition thread"""
    if trigger == 0:
        injector.send_injection()

    for j in range(runs_per_measure):
        if stop_event.is_set():
            return

        board.run()
        errors, info = board.get()
        filename = "attack"
        with open(
            os.path.join(out_directory, f"{filename}.errors.txt"), mode="a"
        ) as file:
            file.write(str(errors) + "\n")
        with open(
            os.path.join(out_directory, f"{filename}.info.txt"), mode="a"
        ) as file:
            file.write(info + "\n")
    injector.stop_injection()


def run_attack(
    board,
    runs_per_measure,
    out_directory,
    injector,
    trigger,
):
    """Run attack in a separate thread

    Args:
        board: device for target board
        runs_per_measure: number of measures to run per point
        out_directory: output directory

    Returns:
        Tuple of (thread, stop_event), required to stop the new thread
    """
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_run_attack_thread,
        args=(
            board,
            runs_per_measure,
            out_directory,
            injector,
            trigger,
            stop_event,
        ),
    )
    thread.start()
    return thread, stop_event


def stop_attack(board, injector, thread, event):
    """Stop the thread which runs the acquisition

    Args:
        board: device for the target board
        thread, event: result of run_acquisition()
    """
    if thread.is_alive():
        board.stop()
        injector.stop_injection()
        event.set()
        while thread.is_alive():
            thread.join()


def parse_out_directory(out_directory):
    """Parse an output directory to retrieve error average

    Args:
        out_directory: output directory in which measures are stored

    Returns:
        Value for error average
    """
    data = {}
    files = [
        f
        for f in os.listdir(out_directory)
        if os.path.isfile(os.path.join(out_directory, f))
    ]

    for file in files:
        with open(os.path.join(out_directory, file)) as f:
            value = 0

            if file.endswith(".errors.txt"):
                lines = f.readlines()
                for line in lines:
                    mean = np.fromstring(line, sep=",").mean()
                    value += mean / len(lines)
            else:
                continue
            data = value

    return data
