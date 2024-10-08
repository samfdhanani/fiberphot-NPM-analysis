import pandas as pd
from scipy.signal import find_peaks
import numpy as np
import os
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Path to the folder containing subject folders
cohort_folder = '/Users/samdhanani/Desktop/MuhleLab/FiberPhotometry/Cohort_G'

# Define the suffix to be used for all new files
suffix = 'thresh0' #description of find_peaks parameters
time = '10min' # or 'all' for uncropped data

# Get a list of subject folders
subject_folders = [folder for folder in os.listdir(cohort_folder) if os.path.isdir(os.path.join(cohort_folder, folder))]

# Initialize lists to store peak data
pre_injection_peak_data = []
post_injection_peak_data = []
full_session_peak_data = []
peak_data = []
auc_data = []

for subject_folder in subject_folders:
    # Construct paths to subject files
    pre_injection_files_folder = os.path.join(cohort_folder, subject_folder, 'pre_injection')
    post_injection_files_folder = os.path.join(cohort_folder, subject_folder, 'post_injection')
    full_session_files_folder = os.path.join(cohort_folder, subject_folder, 'full_session')

    # Check if the pre_injection and post_injection files exist
    pre_injection_file_path = os.path.join(pre_injection_files_folder, f'{subject_folder}_pre_injection_{time}_dFF.csv')
    post_injection_file_path = os.path.join(post_injection_files_folder, f'{subject_folder}_post_injection_{time}_dFF.csv')
    full_session_file_path = os.path.join(full_session_files_folder, f'{subject_folder}_full_session_{time}_dFF.csv')

    # Read the z-scored ΔF/F data
    pre_injection_dFF_df = pd.read_csv(pre_injection_file_path)
    post_injection_dFF_df = pd.read_csv(post_injection_file_path)
    full_session_dFF_df = pd.read_csv(full_session_file_path)

    # Extract Delta_F_over_F and Time columns for each dataset
    pre_injection_dFF = pre_injection_dFF_df['dFF']
    pre_injection_time = pre_injection_dFF_df['x axis']

    post_injection_dFF = post_injection_dFF_df['dFF']
    post_injection_time = post_injection_dFF_df['x axis']

    full_session_dFF = full_session_dFF_df['dFF']
    full_session_time = full_session_dFF_df['x axis']

    # Parameters for peak detection
    height = 0
    sampling_rate = 60  # 60 Hz
    time_interval = 0.1  # Minimum time interval between peaks in seconds
    distance = None # int(time_interval * sampling_rate)

    # Detect peaks for each dataset  
    pre_injection_peaks, _ = find_peaks(pre_injection_dFF, height=height, distance=distance)
    post_injection_peaks, _ = find_peaks(post_injection_dFF, height=height, distance=distance)
    full_session_peaks, _ = find_peaks(full_session_dFF, height=height, distance=distance)

    # Format peak data for pre_injection
    pre_injection_peak_values = pre_injection_dFF.iloc[pre_injection_peaks]
    pre_injection_peak_indices = pre_injection_peaks

    # Format peak data for post_injection
    post_injection_peak_values = post_injection_dFF.iloc[post_injection_peaks]
    post_injection_peak_indices = post_injection_peaks

    # Format peak data for pre_injection
    pre_injection_peak_values = pre_injection_dFF.iloc[pre_injection_peaks]
    pre_injection_peak_indices = pre_injection_peaks
    pre_injection_peak_df = pd.DataFrame({'peak index': pre_injection_peak_indices, 'dFF': pre_injection_peak_values})
    pre_injection_peak_csv_path = os.path.join(pre_injection_files_folder, f'{subject_folder}_pre_injection_peak_values_{time}_{suffix}.csv')
    pre_injection_peak_df.to_csv(pre_injection_peak_csv_path, index=False)
    print(f"pre_injection peak values saved to: {pre_injection_peak_csv_path}")

    # Format peak data for pre_injection
    post_injection_peak_values = post_injection_dFF.iloc[post_injection_peaks]
    post_injection_peak_indices = post_injection_peaks
    post_injection_peak_df = pd.DataFrame({'peak index': post_injection_peak_indices, 'dFF': post_injection_peak_values})
    post_injection_peak_csv_path = os.path.join(post_injection_files_folder, f'{subject_folder}_post_injection_peak_values_{time}_{suffix}.csv')
    post_injection_peak_df.to_csv(post_injection_peak_csv_path, index=False)
    print(f"post_injection peak values saved to: {post_injection_peak_csv_path}")

 # Format peak data for pre_injection
    for i, peak_idx in enumerate(pre_injection_peaks):
        start_time = pre_injection_time.iloc[peak_idx]
        end_time = pre_injection_time.iloc[peak_idx + 1] if peak_idx + 1 < len(pre_injection_time) else np.nan
        if not np.isnan(end_time):  # Ensure end time is valid
            start_dff = pre_injection_dFF.iloc[peak_idx]
            end_dff = pre_injection_dFF.iloc[peak_idx + 1]
            pre_injection_peak_data.append({
                'Peak Number': f'Peak {i + 1}',
                'Start Time': start_time,
                'End Time': end_time,
                'Start dFF': start_dff,
                'End dFF': end_dff
            })

    # Format peak data for post_injection
    for i, peak_idx in enumerate(post_injection_peaks):
        start_time = post_injection_time.iloc[peak_idx]
        end_time = post_injection_time.iloc[peak_idx + 1] if peak_idx + 1 < len(post_injection_time) else np.nan
        if not np.isnan(end_time):  # Ensure end time is valid
            start_dff = post_injection_dFF.iloc[peak_idx]
            end_dff = post_injection_dFF.iloc[peak_idx + 1]
            post_injection_peak_data.append({
                'Peak Number': f'Peak {i + 1}',
                'Start Time': start_time,
                'End Time': end_time,
                'Start dFF': start_dff,
                'End dFF': end_dff
            })

    # Create DataFrames from peak data
    pre_injection_peak_df = pd.DataFrame(pre_injection_peak_data)
    post_injection_peak_df = pd.DataFrame(post_injection_peak_data)

    # Define CSV file paths
    pre_injection_peak_csv_path = os.path.join(pre_injection_files_folder, f'{subject_folder}_pre_injection_peak_startend_{time}_{suffix}.csv')
    post_injection_peak_csv_path = os.path.join(post_injection_files_folder, f'{subject_folder}_post_injection_peak_startend_{time}_{suffix}.csv')

    # Export DataFrames to CSV
    pre_injection_peak_df.to_csv(pre_injection_peak_csv_path, index=False)
    post_injection_peak_df.to_csv(post_injection_peak_csv_path, index=False)

    pre_injection_peak_timestamps = pre_injection_time.iloc[pre_injection_peaks]
    pre_injection_peak_values = pre_injection_dFF.iloc[pre_injection_peaks]

    post_injection_peak_timestamps = post_injection_time.iloc[post_injection_peaks]
    post_injection_peak_values = post_injection_dFF.iloc[post_injection_peaks]

    full_session_peak_timestamps = full_session_time.iloc[full_session_peaks]
    full_session_peak_values = full_session_dFF.iloc[full_session_peaks]

    # Calculate amplitude for each peak individually
    pre_injection_frequency = len(pre_injection_peaks) / (pre_injection_time.iloc[-1] - pre_injection_time.iloc[0])
    pre_injection_indiv_amplitudes = pre_injection_peak_values - pre_injection_peak_values.min()  
    pre_injection_average_amplitude = pre_injection_indiv_amplitudes.mean()

    # Calculate amplitude for each peak individually
    post_injection_frequency = len(post_injection_peaks) / (post_injection_time.iloc[-1] - post_injection_time.iloc[0])
    post_injection_indiv_amplitudes = post_injection_peak_values - post_injection_peak_values.min()  
    post_injection_average_amplitude = post_injection_indiv_amplitudes.mean()

    # Calculate the area under the curve for the post-injection period
    post_injection_peak_auc = 0
    for i in range(len(post_injection_peak_timestamps) - 1):
        peak_start = post_injection_peak_timestamps.iloc[i]
        peak_end = post_injection_peak_timestamps.iloc[i + 1]
        peak_area = np.trapz(post_injection_dFF[(post_injection_time >= peak_start) & (post_injection_time <= peak_end)], 
                             post_injection_time[(post_injection_time >= peak_start) & (post_injection_time <= peak_end)])
        post_injection_peak_auc += peak_area

    # Find the number of peaks
    pre_injection_num_peaks = len(pre_injection_peaks)
    post_injection_num_peaks = len(post_injection_peaks)

    # Find the total time of the pre injection time (used later to find peak rates)
    pre_injection_total_time = np.subtract(pre_injection_dFF_df['ComputerTimestamp'].iloc[-1], pre_injection_dFF_df['ComputerTimestamp'].iloc[0])
    pre_injection_total_time_sec = np.divide(pre_injection_total_time, 1000)
    pre_injection_total_time_min = np.divide(pre_injection_total_time_sec, 60)

    # Find the averages and standard deviation of the dFF values
    pre_injection_average_dFF = pre_injection_dFF.mean()
    pre_injection_std_dFF = pre_injection_dFF.std()

    post_injection_average_dFF = post_injection_dFF.mean()
    post_injection_std_dFF = post_injection_dFF.std()
    
    # Find the number of peaks per second
    pre_injection_peakspersec = np.divide(pre_injection_num_peaks,pre_injection_total_time_sec) 
    pre_injection_peakspermin = np.divide(pre_injection_num_peaks,pre_injection_total_time_min)

    # Organize peak data
    peak_data.append([
        subject_folder,
        'pre_injection',
        pre_injection_average_dFF, 
        pre_injection_std_dFF, 
        pre_injection_num_peaks,
        pre_injection_peakspersec,
        pre_injection_peakspermin,
        pre_injection_frequency, 
        pre_injection_average_amplitude, 
    ])

    # Organize AUC data for post injection
    auc_data.append([
        subject_folder,
        'post_injection',
        post_injection_peak_auc,
    ])

    # Create a DataFrame from all_peak_data and save to a CSV file
    columns = ['Subject Folder', 'Condition', 'Average dFF', 'Std dFF', 'Number of Peaks', 'Peaks per sec', 'Peaks per min','Frequency', 'Average Amplitude']
    peak_df = pd.DataFrame(peak_data, columns=columns)
    peak_csv_path = os.path.join(cohort_folder, f'peak_data_{time}_{suffix}.csv')
    peak_df.to_csv(peak_csv_path, index=False)

    print("All peak data saved to CSV file.")

    columns = ['Subject Folder', 'Condition', 'AUC']
    auc_data_df = pd.DataFrame(auc_data, columns=columns)
    auc_data_csv_path = os.path.join(cohort_folder, f'auc_{time}_{suffix}.csv')
    auc_data_df.to_csv(auc_data_csv_path, index=False)

    print("AUC data for post_injection saved")

    # Save pdf files of the plots
    pre_injection_pdf_file_path = os.path.join(pre_injection_files_folder, subject_folder + f'_plots_dFF_{time}_{suffix}.pdf')
    pre_injection_pdf_pages = PdfPages(pre_injection_pdf_file_path)

    post_injection_pdf_file_path = os.path.join(post_injection_files_folder, subject_folder + f'_plots_dFF_{time}_{suffix}.pdf')
    post_injection_pdf_pages = PdfPages(post_injection_pdf_file_path) 

    full_session_pdf_file_path = os.path.join(full_session_files_folder, subject_folder + f'_plots_dFF_{time}_{suffix}.pdf')
    full_session_pdf_pages = PdfPages(full_session_pdf_file_path)

    # plots the dFF values and mark the detected peaks on the 
    plt.figure(figsize=(12, 6))
    plt.plot(pre_injection_dFF_df['x axis'], pre_injection_dFF_df['dFF'], color='black', linewidth=1)
    plt.plot(pre_injection_peak_timestamps, pre_injection_peak_values, 'ro', markersize=5)  # Mark detected peaks
    plt.title('Detected Peaks for pre_injection')
    plt.xlabel('Time (seconds)')
    plt.ylabel('z-scored ΔF/F values')
    plt.grid(True)
    pre_injection_pdf_pages.savefig()

    plt.figure(figsize=(12, 6))
    plt.plot(post_injection_dFF_df['x axis'], post_injection_dFF_df['dFF'], color='black', linewidth=1)
    plt.plot(post_injection_peak_timestamps, post_injection_peak_values, 'ro', markersize=5)  # Mark detected peaks
    plt.title('Detected Peaks for post_injection')
    plt.xlabel('Time (seconds)')
    plt.ylabel('z-scored ΔF/F values')
    plt.grid(True)
    post_injection_pdf_pages.savefig()

    plt.figure(figsize=(12, 6))
    plt.plot(full_session_dFF_df['x axis'], full_session_dFF_df['dFF'], color='black', linewidth=1)
    plt.plot(full_session_peak_timestamps, full_session_peak_values, 'ro', markersize=5)  # Mark detected peaks
    plt.title('Detected Peaks for full session')
    plt.xlabel('Time (seconds)')
    plt.ylabel('z-scored ΔF/F values')
    plt.grid(True)
    full_session_pdf_pages.savefig()

    pre_injection_pdf_pages.close()
    post_injection_pdf_pages.close()
    full_session_pdf_pages.close()
    plt.close('all')

    # save pre-injection information, the timestamp and amplitudes
    pre_injection_peak_df = pd.DataFrame({'Timestamp': pre_injection_peak_timestamps, 'Amplitude': pre_injection_indiv_amplitudes})
    pre_injection_peak_csv_path = os.path.join(pre_injection_files_folder, f'{subject_folder}_{os.path.basename(pre_injection_files_folder)}_amplitudes_{time}_{suffix}.csv')
    pre_injection_peak_df.to_csv(pre_injection_peak_csv_path, index=False)
    print("pre_injection peak information saved to:", pre_injection_peak_csv_path)
