import time
import numpy as np
import matplotlib.pyplot as plt
from openbci import cyton as bci

data = []

def collect_data(sample):
    global data
    data.append(sample.channels_data)
    if len(data) > 1000:  # Keep only the latest 1000 samples
        data = data[-1000:]

def live_plotter():
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [])

    while True:
        if len(data) > 0:
            y_data = np.array(data)
            line.set_ydata(y_data)
            line.set_xdata(np.arange(len(y_data)))
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.05)

board = bci.OpenBCICyton(port='/dev/ttyUSB0')  # Update with your serial port
board_thread = threading.Thread(target=board.start_stream, args=(collect_data,))
board_thread.start()

live_plotter()