import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


time = '10min' # 'all' for uncropped pre and post injection files
c = None #0      # x axis lower limit
d = None #18000  # x axis upper limit
e = None #-0.5   # y axis lower limit
f = None #0.6    # y axis upper limit
cohort_folder = '/Users/samdhanani/Desktop/MuhleLab/FiberPhotometry/Cohort_G'
subject_folders = [folder for folder in os.listdir(cohort_folder) if os.path.isdir(os.path.join(cohort_folder, folder))]

for subject_folder in subject_folders:
    transformed_files_folder = os.path.join(cohort_folder, subject_folder, 'transformed_files')
    
    plot_file_name = subject_folder + f'_{time}_post_injection.csv'
    plot_file_path = os.path.join(transformed_files_folder, plot_file_name)

    pre_injection_file_name = subject_folder + f'_{time}_pre_injection.csv'
    pre_injection_file_path = os.path.join(transformed_files_folder, pre_injection_file_name)

    post_injection_folder = create_folder(os.path.join(cohort_folder, subject_folder, 'post_injection'))
    pre_injection_folder = create_folder(os.path.join(cohort_folder, subject_folder, 'pre_injection'))

    if not os.path.exists(plot_file_path) or not os.path.exists(pre_injection_file_path):
        print(f"File {plot_file_path} or {pre_injection_file_path} not found. Skipping {subject_folder}.")
        continue

    # Read the CSV files
    df_post = pd.read_csv(plot_file_path)
    df_pre = pd.read_csv(pre_injection_file_path)

    # Save to post_injection folder
    new_file_path_post = os.path.join(post_injection_folder, plot_file_name)
    df_post.to_csv(new_file_path_post, index=False)

    new_file_path_pre = os.path.join(pre_injection_folder, pre_injection_file_name)
    df_pre.to_csv(new_file_path_pre, index=False)

    # Create PDF pages for plots
    pdf_file_path_post = os.path.join(post_injection_folder, subject_folder + f'_plots_post_injection_{time}.pdf')
    pdf_pages_post = PdfPages(pdf_file_path_post)

    pdf_file_path_pre = os.path.join(pre_injection_folder, subject_folder + f'_plots_pre_injection_{time}.pdf')
    pdf_pages_pre = PdfPages(pdf_file_path_pre)

    # Separate reference and signal data based on LedState for pre_injection data
    reference_state_pre = df_pre['LedState'] == 1
    signal_state_pre = df_pre['LedState'] == 2
    raw_reference_pre = df_pre.loc[reference_state_pre, 'G0']
    raw_signal_pre = df_pre.loc[signal_state_pre, 'G0']
    reference_timestamps_pre = df_pre.loc[reference_state_pre, 'ComputerTimestamp']
    signal_timestamps_pre = df_pre.loc[signal_state_pre, 'ComputerTimestamp']

    # Ensure timestamps are aligned for pre_injection data
    reference_timestamps_pre = reference_timestamps_pre.reset_index(drop=True)
    signal_timestamps_pre = signal_timestamps_pre.reset_index(drop=True)

    aligned_reference_pre = raw_reference_pre.reset_index(drop=True).loc[reference_timestamps_pre.index]
    aligned_signal_pre = raw_signal_pre.reset_index(drop=True).loc[signal_timestamps_pre.index]

    # Find the minimum length of the pre_injection datasets
    min_length_pre = min(len(aligned_reference_pre), len(aligned_signal_pre))

    # Truncate the longer pre_injection dataset to match the minimum length
    aligned_reference_pre = aligned_reference_pre[:min_length_pre]
    aligned_signal_pre = aligned_signal_pre[:min_length_pre]
    aligned_timestamps_pre = signal_timestamps_pre[:min_length_pre]

    # Perform linear regression on the pre_injection data
    reg = np.polyfit(aligned_reference_pre, aligned_signal_pre, 1)
    a = reg[0]
    b = reg[1]
    baseline_fit = a * aligned_reference_pre + b

    # Compute the ΔF/F (delta F over F) for the pre_injection data
    dff_baseline = (aligned_signal_pre - baseline_fit) / baseline_fit

    # Separate reference and signal data based on LedState for post-injection data
    reference_state_post = df_post['LedState'] == 1
    signal_state_post = df_post['LedState'] == 2
    raw_reference_post = df_post.loc[reference_state_post, 'G0']
    raw_signal_post = df_post.loc[signal_state_post, 'G0']
    reference_timestamps_post = df_post.loc[reference_state_post, 'ComputerTimestamp']
    signal_timestamps_post = df_post.loc[signal_state_post, 'ComputerTimestamp']

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

    # Apply the linear regression model obtained from the pre_injection data to the post-injection reference data
    post_fit = a * aligned_reference_post + b

    # Compute the ΔF/F (delta F over F) for the post-injection data
    dff_post = (aligned_signal_post - post_fit) / post_fit

    # Create x-axis values as integers from 1 to the length of dff
    x_axis_pre = np.arange(1, len(dff_baseline) + 1)
    x_axis_post = np.arange(1, len(dff_post) + 1)


    # Plot the pre_injection dff values
    plt.figure(figsize=(16, 8))
    plt.plot(x_axis_pre, dff_baseline, 'black', linewidth=1.5)
    plt.xlabel(f'x axis for {time}')
    plt.ylabel('ΔF/F')
    plt.title(f'Pre_injection ΔF/F for {subject_folder}')
    plt.grid(True)
    pdf_pages_pre.savefig()
    pdf_pages_pre.close()
    plt.close()

    # Plot the post-injection dff values
    plt.figure(figsize=(16, 8))
    plt.plot(x_axis_post, dff_post, 'black', linewidth=1.5)
    plt.xlabel(f'x axis for {time}')
    plt.ylabel('ΔF/F')
    plt.title(f'Post-injection ΔF/F for {subject_folder}')
    plt.grid(True)
    pdf_pages_post.savefig()
    pdf_pages_post.close()
    plt.close()

    # Define the output CSV file paths
    csv_file_path_pre_injection = os.path.join(pre_injection_folder, f'{subject_folder}_pre_injection_{time}_dFF.csv')
    csv_file_path_post = os.path.join(post_injection_folder, f'{subject_folder}_post_injection_{time}_dFF.csv')

    # Convert the dff values to DataFrames with x-axis values and ComputerTimestamp
    dff_baseline_df = pd.DataFrame({'x axis': x_axis_pre, 'ComputerTimestamp': aligned_timestamps_pre, 'dFF': dff_baseline})
    dff_post_df = pd.DataFrame({'x axis': x_axis_post, 'ComputerTimestamp': aligned_timestamps_post, 'dFF': dff_post})

    # Export the DataFrames to CSV files
    dff_baseline_df.to_csv(csv_file_path_pre_injection, index=False)
    dff_post_df.to_csv(csv_file_path_post, index=False)
    
    print(f"pre_injection CSV file for {subject_folder} exported successfully!")
    print(f"Post-injection CSV file for {subject_folder} exported successfully!")
