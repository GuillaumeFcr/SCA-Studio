import numpy as np
import os
import threading


def _run_target_board_thread(board, stop_refresh, abort_on_error, stop_event, results):
    """Target board run thread"""
    results[0] = 0
    while not (stop_event.is_set() or (abort_on_error and results[0])):
        board.run()
        results[0] += board.get()[0]
    if abort_on_error:
        stop_refresh()


def run_target_board(board, stop_refresh, abort_on_error):
    """Run target board in a separate thread

    Args:
        board: device for the target board
        stop_refresh: function to call when the thread aborts on error
        abort_on_error: whether the thread should abort on error

    Returns:
        Tuple of (thread, stop_event, results), required to stop the new thread
    """
    stop_event = threading.Event()
    results = [0]
    thread = threading.Thread(
        target=_run_target_board_thread,
        args=(board, stop_refresh, abort_on_error, stop_event, results),
    )
    thread.start()
    return thread, stop_event, results


def stop_target_board(board, thread, stop_event, results):
    """Stop the thread which runs the target board

    Args:
        board: device for the target board
        thread, stop_event, results: result of run_target_board

    Returns:
        Number of errors that occured during the run
    """
    if thread.is_alive():
        board.stop()
        stop_event.set()
        while thread.is_alive():
            thread.join()
    return results[0]


def _run_acquisition_thread(
    board,
    oscilloscope,
    positioning,
    ui_refresher,
    points,
    runs_per_measure,
    out_directory,
    stop_event,
):
    """Acquisition thread"""
    for i, (x, y) in enumerate(points):
        positioning.move(x=x, y=y, absolute=True)
        positioning.wait()
        x, y, _ = positioning.locate()
        ui_refresher(i * runs_per_measure, len(points) * runs_per_measure, (x, y))

        for j in range(runs_per_measure):
            if stop_event.is_set():
                return

            board.run()
            errors, info = board.get()
            data = oscilloscope.get_data()

            filename = f"{x}_{y}"
            with open(os.path.join(out_directory, f"{filename}.measures.txt"), mode="a") as file:
                file.write(",".join(map(str, data)) + "\n")
            with open(os.path.join(out_directory, f"{filename}.errors.txt"), mode="a") as file:
                file.write(str(errors) + "\n")
            with open(os.path.join(out_directory, f"{filename}.info.txt"), mode="a") as file:
                file.write(info + "\n")

            ui_refresher(i * runs_per_measure + j + 1, len(points) * runs_per_measure, (x, y))


def run_acquisition(
    board,
    oscilloscope,
    positioning,
    ui_refresher,
    points,
    runs_per_measure,
    out_directory,
):
    """Run acquisition in a separate thread

    Args:
        board: device for target board
        oscilloscope: device for oscilloscope
        positioning: device for positioning system
        ui_refresher: function to call to refresh the ui during the acquisition
        points: list of (x,y) coordinates to go to during the acquisition
        runs_per_measure: number of measures to run per point
        out_directory: output directory

    Returns:
        Tuple of (thread, stop_event), required to stop the new thread
    """
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_run_acquisition_thread,
        args=(
            board,
            oscilloscope,
            positioning,
            ui_refresher,
            points,
            runs_per_measure,
            out_directory,
            stop_event,
        ),
    )
    thread.start()
    return thread, stop_event


def stop_acquisition(board, thread, event):
    """Stop the thread which runs the acquisition

    Args:
        board: device for the target board
        thread, event: result of run_acquisition()
    """
    if thread.is_alive():
        board.stop()
        event.set()
        while thread.is_alive():
            thread.join()


def parse_out_directory(out_directory, errors_data):
    """Parse an output directory to retrieve measure intensity or error mean for each point

    Args:
        out_directory: output directory in which measures are stored
        errors_data: count errors instead of measured data

    Returns:
        Dict of {(x,y): value} with value for each (x,y) coordinates
    """
    data = {}
    files = [f for f in os.listdir(out_directory) if os.path.isfile(os.path.join(out_directory, f))]

    for file in files:
        with open(os.path.join(out_directory, file)) as f:
            value = 0

            if file.endswith(".errors.txt") and errors_data:
                lines = f.readlines()
                for line in lines:
                    mean = np.fromstring(line, sep=",").mean()
                    value += mean / len(lines)

            elif file.endswith(".measures.txt") and not errors_data:
                lines = f.readlines()
                for line in lines:
                    measure = np.fromstring(line, sep=",")
                    val = np.mean(np.abs(measure - measure.mean()))  # recenter measure and get mean of absolute
                    value += val / len(lines)

            else:
                continue

            coords = file.replace(".errors.txt", "").replace(".measures.txt", "").split("_")
            x, y = float(coords[0]), float(coords[1])
            data[(x, y)] = value

    return data
