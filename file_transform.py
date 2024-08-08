import pandas as pd
import numpy as np
import os

def create_transformed_files_folder(subject_folder_path):
    transformed_files_folder = os.path.join(subject_folder_path, 'transformed_files')
    if not os.path.exists(transformed_files_folder):
        os.makedirs(transformed_files_folder)
    return transformed_files_folder

# Path to the folder containing subject folders
cohort_folder = '/Users/samdhanani/Desktop/MuhleLab/FiberPhotometry/Cohort_G' # '/filepath/folder containing subject folder(s)'
# Get a list of subject folders
subject_folders = [folder for folder in os.listdir(cohort_folder) if os.path.isdir(os.path.join(cohort_folder, folder))]

for subject_folder in subject_folders:
    subject_folder_path = os.path.join(cohort_folder, subject_folder)
    # create folder to store all outputs from this code
    transformed_files_folder = create_transformed_files_folder(subject_folder_path)
    
    # create file paths
    csv_file_path = os.path.join(subject_folder_path, subject_folder + '.csv')
    handle_file_path = os.path.join(subject_folder_path, subject_folder + 'Handle.csv')
    injection_file_path = os.path.join(subject_folder_path, subject_folder + 'Injection.csv')
    start_file_path = os.path.join(subject_folder_path, subject_folder + 'Start.csv')

    # define dataframes of bonsai output files
    csv_file_df = pd.read_csv(csv_file_path)
    start_time_df = pd.read_csv(start_file_path, header=None, names=['Item1', 'Item2'])
    handle_df = pd.read_csv(handle_file_path, header=None, names=['Item1', 'Item2'])

    x = 10  # Set the number of minutes for the time interval of the pre and post injection periods!
    frame_rate_hz = 60 # set the frame rate here! 

    # remove photobleaching data
    start_timestamp = start_time_df.loc[start_time_df['Item1'] == 'S', 'Item2'].values
    if len(start_timestamp) > 0:
        start_timestamp = float(start_timestamp[0])  # Convert to float if not already
        print("Start Timestamp:", start_timestamp)
        photobleach_removed_df = csv_file_df[csv_file_df['ComputerTimestamp'] >= start_timestamp]
        photobleach_removed_file_path = os.path.join(transformed_files_folder, subject_folder + '_photobleach_removed.csv')
        photobleach_removed_df.to_csv(photobleach_removed_file_path, index=False)
        print("Data with photobleaching removed:", photobleach_removed_file_path)
    else:
        print("Error removing photobleaching")



    '''
                            removing the photobleaching and handling
    '''



    # removing the handling: step 1 make a list of ranges to be excluded
    exclusion_ranges = []
    handle_start = None
    for index, row in handle_df.iterrows():
        if row['Item1'] == 'H' and handle_start is None:
            handle_start = row['Item2']
        elif row['Item1'] == 'H' and handle_start is not None:
            exclusion_ranges.append((handle_start, row['Item2']))
            handle_start = None

    # removing the handling: step 2 filter out the exclusion ranges 
    photobleach_handle_removed_df = photobleach_removed_df.copy()
    for range_start, range_end in exclusion_ranges:
        range_start = float(range_start)
        range_end = float(range_end)
        photobleach_handle_removed_df = photobleach_handle_removed_df[
            (photobleach_handle_removed_df['ComputerTimestamp'].astype(float) < range_start) |
            (photobleach_handle_removed_df['ComputerTimestamp'].astype(float) > range_end)
        ]

    # removing the handling: step 3 remove occurances of consecutive led states
    remove_led = []
    for i in range(len(photobleach_handle_removed_df) - 1):
        current_led = photobleach_handle_removed_df.iloc[i]['LedState']
        next_led = photobleach_handle_removed_df.iloc[i + 1]['LedState']
        if current_led == next_led:
            if current_led == 1:
                remove_led.append(photobleach_handle_removed_df.index[i])  # Drop the first occurrence
            elif current_led == 2:
                remove_led.append(photobleach_handle_removed_df.index[i + 1])  # Drop the second occurrence
    photobleach_handle_removed_df.drop(remove_led, inplace=True)

    # removing the handling: step 4 add an arbitrary x axis to the data to plot
    photobleach_handle_removed_df['reference x axis'] = np.nan
    photobleach_handle_removed_df['signal x axis'] = np.nan
    reference_state = photobleach_handle_removed_df['LedState'] == 1
    signal_state = photobleach_handle_removed_df['LedState'] == 2
    raw_reference = photobleach_handle_removed_df.loc[reference_state, 'G0']
    raw_signal = photobleach_handle_removed_df.loc[signal_state, 'G0']
    photobleach_handle_removed_df.loc[reference_state, 'reference x axis'] = np.arange(1, len(raw_reference) + 1)
    photobleach_handle_removed_df.loc[signal_state, 'signal x axis'] = np.arange(1, len(raw_signal) + 1)
    photobleach_handle_removed_file_path = os.path.join(transformed_files_folder, subject_folder + '_photobleach_handle_removed.csv')
    photobleach_handle_removed_df.to_csv(photobleach_handle_removed_file_path, index=False)
    print("data with photobleaching and handling removed saved to:", photobleach_handle_removed_file_path)



    '''
                            interpolate the data and add arbitrary x-axis
    '''



    # Separate raw data and timestamps for reference and signal
    reference_state = photobleach_handle_removed_df['LedState'] == 1
    signal_state = photobleach_handle_removed_df['LedState'] == 2
    raw_reference = photobleach_handle_removed_df.loc[reference_state, 'G0']
    raw_signal = photobleach_handle_removed_df.loc[signal_state, 'G0']
    reference_timestamps = photobleach_handle_removed_df.loc[reference_state, 'ComputerTimestamp']
    signal_timestamps = photobleach_handle_removed_df.loc[signal_state, 'ComputerTimestamp']
    system_timestamp = photobleach_handle_removed_df['SystemTimestamp']
    frame_counter = photobleach_handle_removed_df['FrameCounter']
    all_timestamps = photobleach_handle_removed_df['ComputerTimestamp']

    interpolated_reference = np.interp(all_timestamps, reference_timestamps, raw_reference)
    interpolated_signal = np.interp(all_timestamps, signal_timestamps, raw_signal)

    num_samples = len(all_timestamps)
    x_axis = np.arange(1, num_samples + 1)
    combined_df = pd.DataFrame({
        'FrameCounter': frame_counter,
        'SystemTimestamp': system_timestamp,
        'ComputerTimestamp': all_timestamps,
        'Reference x axis': x_axis,
        'Reference G0': interpolated_reference,
        'Signal x axis': x_axis,
        'Signal G0': interpolated_signal
    })
    interpolated_file_path = os.path.join(transformed_files_folder, subject_folder + '_interpolated.csv')
    combined_df.to_csv(interpolated_file_path, index=False)
    print("Photobleach and handle removed data saved to:", interpolated_file_path)



    '''
                            make baseline, amph, and full session csv files
    '''



    injection_df = pd.read_csv(injection_file_path, header=None, names=['Item1', 'Item2'])
    pre_injection_timestamp = injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[0]
    post_injection_timestamp = injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[1]

    pre_injection_timestamp_ms = float(pre_injection_timestamp)
    post_injection_timestamp_ms = float(post_injection_timestamp)

    pre_injection_df = photobleach_handle_removed_df[photobleach_handle_removed_df['ComputerTimestamp'] <= pre_injection_timestamp_ms]
    post_injection_df = photobleach_handle_removed_df[photobleach_handle_removed_df['ComputerTimestamp'] >= post_injection_timestamp_ms]
    noinjection_df = photobleach_handle_removed_df[(photobleach_handle_removed_df['ComputerTimestamp'] <= pre_injection_timestamp_ms) | 
                                            (photobleach_handle_removed_df['ComputerTimestamp'] >= post_injection_timestamp_ms)]

    pre_injection_file_path = os.path.join(transformed_files_folder, subject_folder + '_all_pre_injection.csv')
    post_injection_file_path = os.path.join(transformed_files_folder, subject_folder + '_all_post_injection.csv')
    noinjection_full_session_file_path = os.path.join(transformed_files_folder, subject_folder + '_all_full_session.csv')

    pre_injection_df.to_csv(pre_injection_file_path, index=False)
    post_injection_df.to_csv(post_injection_file_path, index=False)
    noinjection_df.to_csv(noinjection_full_session_file_path, index=False)
    print("pre-injection data saved to:", pre_injection_file_path)
    print("post-injection data saved to:", post_injection_file_path)
    print("full session data saved to:", noinjection_full_session_file_path)



    '''
                            pull out X min intervals for pre and post injection
    '''



    rows_per_minute = frame_rate_hz * 60
    num_rows_interval = x * rows_per_minute

    pre_injection_start_index = max(pre_injection_df.index[-1] - num_rows_interval, pre_injection_df.index[0])
    interval_pre_injection_df = pre_injection_df.loc[pre_injection_start_index:pre_injection_df.index[-1]]

    post_injection_end_index = min(post_injection_df.index[0] + num_rows_interval, post_injection_df.index[-1])
    interval_post_injection_df = post_injection_df.loc[post_injection_df.index[0]:post_injection_end_index]

    interval_pre_injection_file_path = os.path.join(transformed_files_folder, subject_folder + f'_{x}min_pre_injection.csv')
    interval_post_injection_file_path = os.path.join(transformed_files_folder, subject_folder + f'_{x}min_post_injection.csv')

    interval_pre_injection_df.to_csv(interval_pre_injection_file_path, index=False)
    interval_post_injection_df.to_csv(interval_post_injection_file_path, index=False)

    print(f"{x} minutes before pre-injection data saved to:", interval_pre_injection_file_path)
    print(f"{x} minutes after post-injection data saved to:", interval_post_injection_file_path)

    full_session_df = pd.concat([interval_pre_injection_df, interval_post_injection_df], ignore_index=True)
    full_session_file_path = os.path.join(transformed_files_folder, subject_folder + f'_{x}min_full_session.csv')
    full_session_df.to_csv(full_session_file_path, index=False)

    print(f"Combined pre and post-injection data saved to:", full_session_file_path)


    '''
                            time subtracted values
    '''


    
    def calculate_total_time_difference(handle_df, post_injection_end_time):
        # Convert 'Item2' column to numeric type
        handle_df['Item2'] = pd.to_numeric(handle_df['Item2'], errors='coerce')
        handle_df.dropna(subset=['Item2'], inplace=True)
        # Initialize a variable to store the total time difference
        total_time_difference = 0

        # Iterate over the DataFrame by pairs of rows
        for i in range(0, len(handle_df) - 1, 2):
            start_time = handle_df.iloc[i]['Item2']
            end_time = handle_df.iloc[i + 1]['Item2']
            # Only consider pairs where both start and end timestamps are greater than post_injection_end_time
            if start_time > post_injection_end_time and end_time > post_injection_end_time:
                # Calculate the time difference between consecutive rows
                diff = end_time - start_time
                # Add the calculated difference to the total time difference
                total_time_difference += diff
        return total_time_difference 

    # Calculate total time difference considering post-injection end time
    post_injection_end_time = post_injection_timestamp_ms
    total_time_difference = calculate_total_time_difference(handle_df, post_injection_end_time)

    # Save the result to a CSV file
    filtered_csv_path = os.path.join(transformed_files_folder, subject_folder + '_time_subtracted_values_amph.csv')
    with open(filtered_csv_path, 'w') as f:
        f.write(f'Total Time Difference (ms)\n{total_time_difference}')

    print("Time subtracted values saved to:", filtered_csv_path)