import pandas as pd
import numpy as np
import os

def create_transformed_files_folder(subject_folder_path):
    transformed_files_folder = os.path.join(subject_folder_path, 'transformed_files')
    if not os.path.exists(transformed_files_folder):
        os.makedirs(transformed_files_folder)
    return transformed_files_folder

# path to the folder containing subject folders
cohort_folder = '/Users/samdhanani/Desktop/MuhleLab/FiberPhotometry/Cohort_G' # '/filepath/folder containing subject folder(s)'
# get a list of subject folders
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

    x = 10  # set the number of minutes for the time interval of the pre and post injection periods!
    frame_rate_hz = 60 # set the frame rate here! 

    # remove photobleaching data
    start_timestamp = start_time_df.loc[start_time_df['Item1'] == 'S', 'Item2'].values
    if len(start_timestamp) > 0:  # makes sure there is a start_timestamp
        start_timestamp = float(start_timestamp[0])  # convert from a string to a float
        print("Start Timestamp:", start_timestamp) 
        photobleach_removed_df = csv_file_df[csv_file_df['ComputerTimestamp'] >= start_timestamp] # make new dataframe with rows containing a computer timestamp larger than the start timestamp
        photobleach_removed_file_path = os.path.join(transformed_files_folder, subject_folder + '_photobleach_removed.csv')
        photobleach_removed_df.to_csv(photobleach_removed_file_path, index=False) 
        # always saves a new csv file to the transformed_files folder!
        print("Data with photobleaching removed:", photobleach_removed_file_path)
    else:
        print("Error removing photobleaching")



    '''
                            removing the photobleaching and handling
    '''



    # removing the handling: step 1 make a list of ranges to be excluded
    # assumes row 1 is the start time for the first period of handling and row 2 is the end time for the first period of handling
    exclusion_ranges = [] # list of ranges to be removed from the dataframe
    handle_start = None # tracks start times for handling
    for index, row in handle_df.iterrows(): # iterate over rows in dataframe as pairs
        if row['Item1'] == 'H' and handle_start is None:
            handle_start = row['Item2'] # adds the first row
        elif row['Item1'] == 'H' and handle_start is not None:
            exclusion_ranges.append((handle_start, row['Item2'])) # adds the second row, exclusion ranges are saved
            handle_start = None # resets handle_start to repeat with row 3

    # removing the handling: step 2 filter out the exclusion ranges 
    photobleach_handle_removed_df = photobleach_removed_df.copy()
    for range_start, range_end in exclusion_ranges:
        range_start = float(range_start) # convert from string to float
        range_end = float(range_end)
        photobleach_handle_removed_df = photobleach_handle_removed_df[
            (photobleach_handle_removed_df['ComputerTimestamp'].astype(float) < range_start) |
            (photobleach_handle_removed_df['ComputerTimestamp'].astype(float) > range_end)
        ] # remove times less than the range start and greater than the range end

    # removing the handling: step 3 remove occurances of consecutive led states
    remove_led = [] # stores rows to be removed
    for i in range(len(photobleach_handle_removed_df) - 1): # compares each row with the next row
        current_led = photobleach_handle_removed_df.iloc[i]['LedState'] 
        next_led = photobleach_handle_removed_df.iloc[i + 1]['LedState']
        if current_led == next_led: # if there are 2 LED states in a row then add row to index to be removed
            if current_led == 1:
                remove_led.append(photobleach_handle_removed_df.index[i])  # drop the first occurrence
            elif current_led == 2:
                remove_led.append(photobleach_handle_removed_df.index[i + 1])  # drop the second occurrence
    photobleach_handle_removed_df.drop(remove_led, inplace=True) # drop rows stored in remove_led

    # removing the handling: step 4 add an arbitrary x axis to the reference and the signal data to plot
    photobleach_handle_removed_df['reference x axis'] = np.nan 
    photobleach_handle_removed_df['signal x axis'] = np.nan
    reference_state = photobleach_handle_removed_df['LedState'] == 1
    signal_state = photobleach_handle_removed_df['LedState'] == 2
    raw_reference = photobleach_handle_removed_df.loc[reference_state, 'G0']
    raw_signal = photobleach_handle_removed_df.loc[signal_state, 'G0']
    photobleach_handle_removed_df.loc[reference_state, 'reference x axis'] = np.arange(1, len(raw_reference) + 1)
    photobleach_handle_removed_df.loc[signal_state, 'signal x axis'] = np.arange(1, len(raw_signal) + 1)
    photobleach_handle_removed_file_path = os.path.join(transformed_files_folder, subject_folder + '_photobleach_handle_removed.csv') # save to transformed_files folder
    photobleach_handle_removed_df.to_csv(photobleach_handle_removed_file_path, index=False)
    print("data with photobleaching and handling removed saved to:", photobleach_handle_removed_file_path)



    '''
                            interpolate the data and add arbitrary x-axis
    '''



    # separate raw data and timestamps for reference and signal
    reference_state = photobleach_handle_removed_df['LedState'] == 1 # deinterleave the data 
    signal_state = photobleach_handle_removed_df['LedState'] == 2
    raw_reference = photobleach_handle_removed_df.loc[reference_state, 'G0']
    raw_signal = photobleach_handle_removed_df.loc[signal_state, 'G0']
    reference_timestamps = photobleach_handle_removed_df.loc[reference_state, 'ComputerTimestamp']
    signal_timestamps = photobleach_handle_removed_df.loc[signal_state, 'ComputerTimestamp']
    system_timestamp = photobleach_handle_removed_df['SystemTimestamp'] # keeps the original datapoints
    frame_counter = photobleach_handle_removed_df['FrameCounter']
    all_timestamps = photobleach_handle_removed_df['ComputerTimestamp']

    interpolated_reference = np.interp(all_timestamps, reference_timestamps, raw_reference) # interpolate the reference and signal data
    interpolated_signal = np.interp(all_timestamps, signal_timestamps, raw_signal)

    num_samples = len(all_timestamps) 
    x_axis = np.arange(1, num_samples + 1) # maes an arbitrary x-axis for easier plotting in the future
    interleaved_df = pd.DataFrame({ # reorganize the new csv output
        'FrameCounter': frame_counter,
        'SystemTimestamp': system_timestamp,
        'ComputerTimestamp': all_timestamps,
        'Reference x axis': x_axis,
        'Reference G0': interpolated_reference,
        'Signal x axis': x_axis,
        'Signal G0': interpolated_signal
    })
    interpolated_file_path = os.path.join(transformed_files_folder, subject_folder + '_interpolated.csv')
    interleaved_df.to_csv(interpolated_file_path, index=False)
    print("Photobleach and handle removed data saved to:", interpolated_file_path)



    '''
                            make baseline, post-injection, and full session csv files
                            analyzes the non-interpolated data, change dataframe name to analyze
    '''



    injection_df = pd.read_csv(injection_file_path, header=None, names=['Item1', 'Item2'])
    pre_injection_timestamp = injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[0] # identify the first row as the start of the injection
    post_injection_timestamp = injection_df.loc[injection_df['Item1'] == 'A', 'Item2'].values[1] # identify the first row as the end of the injection

    pre_injection_timestamp_ms = float(pre_injection_timestamp)
    post_injection_timestamp_ms = float(post_injection_timestamp)

    pre_injection_df = photobleach_handle_removed_df[photobleach_handle_removed_df['ComputerTimestamp'] <= pre_injection_timestamp_ms] # define the pre-injection time as rows before the start of the injection
    post_injection_df = photobleach_handle_removed_df[photobleach_handle_removed_df['ComputerTimestamp'] >= post_injection_timestamp_ms] # define the pre-injection time as rows after the end of the injection
    noinjection_df = photobleach_handle_removed_df[(photobleach_handle_removed_df['ComputerTimestamp'] <= pre_injection_timestamp_ms) | 
                                            (photobleach_handle_removed_df['ComputerTimestamp'] >= post_injection_timestamp_ms)]
                                            # define the full session dataframe as the time around the injection

    pre_injection_file_path = os.path.join(transformed_files_folder, subject_folder + '_all_pre_injection.csv') # save to transformed_files folder
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



    rows_per_minute = frame_rate_hz * 60 # uses sampling rate to calculate the number of rows to pull out for 1 minute
    num_rows_interval = x * rows_per_minute # calculates the number of rows to pull from the data so that the same number of rows is extracted for pre and post injection dataframes

    pre_injection_start_index = max(pre_injection_df.index[-1] - num_rows_interval, pre_injection_df.index[0]) # finds the start index, where the interval should start 
    interval_pre_injection_df = pre_injection_df.loc[pre_injection_start_index:pre_injection_df.index[-1]] # data frame is made up of rows from the start index to the last row of the dataframe

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
        # convert 'Item2' column to numeric type
        handle_df['Item2'] = pd.to_numeric(handle_df['Item2'], errors='coerce')
        handle_df.dropna(subset=['Item2'], inplace=True)
        # initialize a variable to store the total time difference
        total_time_difference = 0

        # iterate over the DataFrame by pairs of rows
        for i in range(0, len(handle_df) - 1, 2):
            start_time = handle_df.iloc[i]['Item2']
            end_time = handle_df.iloc[i + 1]['Item2']
            # only consider pairs where both start and end timestamps are greater than post_injection_end_time
            if start_time > post_injection_end_time and end_time > post_injection_end_time:
                # calculate the time difference between consecutive rows
                diff = end_time - start_time
                # add the calculated difference to the total time difference
                total_time_difference += diff
        return total_time_difference 

    # calculate total time difference considering post-injection end time
    post_injection_end_time = post_injection_timestamp_ms
    total_time_difference = calculate_total_time_difference(handle_df, post_injection_end_time)

    # save the result to a CSV file
    filtered_csv_path = os.path.join(transformed_files_folder, subject_folder + '_time_subtracted_values_post_injection.csv')
    with open(filtered_csv_path, 'w') as f:
        f.write(f'Total Time Difference (ms)\n{total_time_difference}')

    print("Time subtracted values saved to:", filtered_csv_path)
