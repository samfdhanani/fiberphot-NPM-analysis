import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

type = 'full_session'
time = '10min' # 'all' for uncropped full session file
c = None #0      # x axis lower limit
d = None #36000  # x axis upper limit
e = None #-0.05   # y axis lower limit
f = None #0.15    # y axis upper limit

cohort_folder = '/Users/samdhanani/Desktop/MuhleLab/FiberPhotometry/Cohort_G'
subject_folders = [folder for folder in os.listdir(cohort_folder) if os.path.isdir(os.path.join(cohort_folder, folder))]

for subject_folder in subject_folders:
    subject_folder_path = os.path.join(cohort_folder, subject_folder)
    transformed_files_folder = os.path.join(subject_folder_path, 'transformed_files')
    
    fullsess_file_name = subject_folder + f'_{time}_full_session.csv'
    fullsess_file_path = os.path.join(transformed_files_folder, fullsess_file_name)

    injection_file_path = os.path.join(subject_folder_path, subject_folder + 'Injection.csv')

    full_session_folder = create_folder(os.path.join(cohort_folder, subject_folder, type))

    if not os.path.exists(fullsess_file_path) or not os.path.exists(injection_file_path):
        print(f"File {fullsess_file_path} or {injection_file_path} not found. Skipping {subject_folder}.")
        continue

    # Read the full session CSV file
    df_fullsess = pd.read_csv(fullsess_file_path)

    # Read the injection file and get the timestamps
    injection_df = pd.read_csv(injection_file_path, header=None, names=['Item1', 'Item2'])
    pre_injection_timestamp = float(injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[0])
    post_injection_timestamp = float(injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[1])

    # Split the data into pre-injection and post-injection
    df_pre_injection = df_fullsess[df_fullsess['ComputerTimestamp'] < pre_injection_timestamp]
    df_post_injection = df_fullsess[df_fullsess['ComputerTimestamp'] > post_injection_timestamp]

    # Separate reference and signal data based on LedState for pre-injection data
    reference_state_pre = df_pre_injection['LedState'] == 1
    signal_state_pre = df_pre_injection['LedState'] == 2
    raw_reference_pre = df_pre_injection.loc[reference_state_pre, 'G0']
    raw_signal_pre = df_pre_injection.loc[signal_state_pre, 'G0']
    reference_timestamps_pre = df_pre_injection.loc[reference_state_pre, 'ComputerTimestamp']
    signal_timestamps_pre = df_pre_injection.loc[signal_state_pre, 'ComputerTimestamp']

    # Ensure timestamps are aligned for pre-injection data
    reference_timestamps_pre = reference_timestamps_pre.reset_index(drop=True)
    signal_timestamps_pre = signal_timestamps_pre.reset_index(drop=True)

    aligned_reference_pre = raw_reference_pre.reset_index(drop=True).loc[reference_timestamps_pre.index]
    aligned_signal_pre = raw_signal_pre.reset_index(drop=True).loc[signal_timestamps_pre.index]


    # Find the minimum length of the pre-injection datasets
    min_length_pre = min(len(aligned_reference_pre), len(aligned_signal_pre))

    # Truncate the longer pre-injection dataset to match the minimum length
    aligned_reference_pre = aligned_reference_pre[:min_length_pre]
    aligned_signal_pre = aligned_signal_pre[:min_length_pre]
    aligned_timestamps_pre = signal_timestamps_pre[:min_length_pre]

    # Perform linear regression on the pre-injection data
    reg = np.polyfit(aligned_reference_pre, aligned_signal_pre, 1)
    a = reg[0]
    b = reg[1]
    pre_injection_fit = a * aligned_reference_pre + b

    # Calculate ΔF/F for pre-injection data
    dff_pre = (aligned_signal_pre - pre_injection_fit) / pre_injection_fit

    # Separate reference and signal data based on LedState for post-injection data
    reference_state_post = df_post_injection['LedState'] == 1
    signal_state_post = df_post_injection['LedState'] == 2
    raw_reference_post = df_post_injection.loc[reference_state_post, 'G0']
    raw_signal_post = df_post_injection.loc[signal_state_post, 'G0']
    reference_timestamps_post = df_post_injection.loc[reference_state_post, 'ComputerTimestamp']
    signal_timestamps_post = df_post_injection.loc[signal_state_post, 'ComputerTimestamp']

    # Ensure timestamps are aligned for post-injection data
    reference_timestamps_post = reference_timestamps_post.reset_index(drop=True)
    signal_timestamps_post = signal_timestamps_post.reset_index(drop=True)

    aligned_reference_post = raw_reference_post.reset_index(drop=True).loc[reference_timestamps_post.index]
    aligned_signal_post = raw_signal_post.reset_index(drop=True).loc[signal_timestamps_post.index]
    

    # Find the minimum length of the post-injection datasets
    min_length_post = min(len(aligned_reference_post), len(aligned_signal_post))
    

    # Truncate the longer post-injection dataset to match the minimum length
    aligned_reference_post = aligned_reference_post[:min_length_post]
    aligned_signal_post = aligned_signal_post[:min_length_post]
    aligned_timestamps_post = signal_timestamps_post[:min_length_post]

    # Apply the linear regression model obtained from the pre-injection data to the post-injection reference data
    post_fit = a * aligned_reference_post + b

    # Compute the ΔF/F (delta F over F) for the post-injection data
    dff_post = (aligned_signal_post - post_fit) / post_fit

    # Combine pre-injection and post-injection ΔF/F data
    dff = np.concatenate([dff_pre, dff_post])
    combined_timestamps = np.concatenate([aligned_timestamps_pre, aligned_timestamps_post])

    # Find the x-axis value closest to the pre-injection timestamp
    pre_injection_index = (np.abs(combined_timestamps - pre_injection_timestamp)).argmin()

    # Create x-axis values as integers from 1 to the length of dff
    x_axis = np.arange(1, len(dff) + 1)

    # Plot the dff values
    plt.figure(figsize=(16, 8))
    plt.plot(x_axis, dff, 'black', linewidth=1.5)
    plt.axvline(x=pre_injection_index + 1, color='red', linestyle='--', linewidth=2, label='Injection Time')
    plt.xlabel(f'x axis for {time}')
    plt.ylabel('ΔF/F')
    plt.xlim(c,d)
    plt.ylim(e,f)
    plt.title(f'ΔF/F for {subject_folder}')
    plt.grid(True)
    plt.legend()

    # Save plot to PDF
    pdf_file_path = os.path.join(full_session_folder, subject_folder + f'_plots_{type}_{time}.pdf')
    pdf_pages = PdfPages(pdf_file_path)
    pdf_pages.savefig()
    pdf_pages.close()

    # Define the output CSV file path
    csv_file_path = os.path.join(full_session_folder, f'{subject_folder}_{type}_{time}_dFF.csv')
    # Convert the dff values to a DataFrame with x-axis and timestamps
    
    dff_df = pd.DataFrame({'x axis': x_axis, 'ComputerTimestamp': combined_timestamps, 'dFF': dff})
    # Export the DataFrame to a CSV file
    dff_df.to_csv(csv_file_path, index=False)
    print(f"CSV file for {subject_folder} exported successfully!")

    print(len(aligned_reference_post))
    print(len(aligned_reference_pre))
    print(len(aligned_signal_post))
    print(len(aligned_signal_pre))

    
