import time
import numpy as np
import pyedflib
from openbci import cyton as bci

data = []
channels = 8  # Number of EEG channels you are using

def collect_data(sample):
    global data
    data.append(sample.channels_data)
    if len(data) > 1000:  # Adjust according to your needs
        data = data[-1000:]

def save_to_edf(data, filename='eeg_data.edf', sfreq=250):
    n_channels = len(data[0])
    n_samples = len(data)

    channel_names = ['ch' + str(i) for i in range(1, n_channels + 1)]
    channel_info = [{'label': name, 'dimension': 'uV', 'sample_rate': sfreq, 'physical_max': 1000, 'physical_min': -1000, 'digital_max': 32767, 'digital_min': -32768} for name in channel_names]

    signal_headers = []
    for info in channel_info:
        signal_headers.append(pyedflib.EdfWriter.make_signal_header(info['label'], dimension=info['dimension'], sample_rate=info['sample_rate'], physical_min=info['physical_min'], physical_max=info['physical_max'], digital_min=info['digital_min'], digital_max=info['digital_max']))

    with pyedflib.EdfWriter(filename, n_channels=n_channels, file_type=pyedflib.FILETYPE_EDFPLUS) as f:
        f.setSignalHeaders(signal_headers)
        f.writeSamples(np.array(data).T)

# Collect EEG data
board = bci.OpenBCICyton(port='/dev/ttyUSB0')  # Update with your serial port
board_thread = threading.Thread(target=board.start_stream, args=(collect_data,))
board_thread.start()

# Collect data for a specific duration
time.sleep(10)  # Collect data for 10 seconds
board.stop_stream()

# Save the collected data to an EDF file
save_to_edf(data) 
