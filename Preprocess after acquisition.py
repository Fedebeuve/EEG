import mne
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy.signal import butter, filtfilt
import os

# Define the base directory where your files are located
base_dir = r'F:\Sleep Data base\cap-sleep-database-1.0.0\3-5-10-11-HC'

# Define function to load sleep stage annotations from a text file
def load_sleep_stages(file_path):
    stages = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                stages.append(int(line.strip().split()[-1]))  # Adjust parsing logic based on file format
            except ValueError:
                continue  # Skip lines that do not contain an integer
    return np.array(stages)

# Define bandpass filter function
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

# Optimized function to calculate PLV
def calculate_plv(data):
    num_channels = data.shape[0]
    num_samples = data.shape[1]
    plv_matrix = np.zeros((num_channels, num_channels))

    for i in range(num_channels):
        for j in range(i+1, num_channels):
            phase_diff = np.angle(data[i]) - np.angle(data[j])
            plv = np.abs(np.mean(np.exp(1j * phase_diff)))
            plv_matrix[i, j] = plv
            plv_matrix[j, i] = plv

    return plv_matrix

# Load and preprocess data for each subject
subject_ids = ['n3', 'n5', 'n10', 'n11']
preprocessed_data = {}
labels = {}

for subj_id in subject_ids:
    # Load EEG data
    eeg_file = os.path.join(base_dir, f'{subj_id}.edf')
    raw = mne.io.read_raw_edf(eeg_file, preload=True)
    
    # Load sleep stages
    stages_file = os.path.join(base_dir, f'{subj_id}.edf.st')
    sleep_stages = load_sleep_stages(stages_file)
    
    # Apply band-pass filtering
    raw.filter(0.5, 40, fir_design='firwin')
    
    # Apply ICA for artifact removal
    ica = mne.preprocessing.ICA(n_components=12, random_state=97)
    ica.fit(raw)
    raw_ica = ica.apply(raw.copy())
    
    # Segment the data into 30-second epochs
    epochs = mne.make_fixed_length_epochs(raw_ica, duration=30, preload=True)
    
    # Store preprocessed data and labels
    preprocessed_data[subj_id] = epochs.get_data()
    labels[subj_id] = sleep_stages