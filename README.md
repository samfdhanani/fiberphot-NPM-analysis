# Analyzing Neurophotometrics FP3002 data with Python.

## The Bonsai workflow
All node structures and workflows are from the Neurophotmetrics Bonsai Textbook linked here:
https://static1.squarespace.com/static/60ff345fca665d50e1adc805/t/65366fc82f93fd1b67b65a5b/1698066378544/BonsaiGuide_20231023.pdf

**Outputs**
1. SubjectID.csv
   - the raw data file.
2. SubjectIDStart.csv
   - a file containing the timestamp of when you want to start the session after a period of photobleaching.
3. SubjectIDInjection.csv
   - a file containing two timestamps, one right before you pick up the mouse to administer and injection and the second after the mouse is placed in the open field following the injection.
4. SubjectIDHandle.csv
   - this file contains pairs of timestamps indicating the times before and after manually handling a mouse in the open field. 

## Transforming the data files before plotting and calculating the zdFF scores

**Reading the Bonsai Outputs**

- The script defines a cohort folder and a subject folder which is used to locate the data and analyze multiple subjects in a row within the cohort folder. The outputs (SubjectIDStart.csv, SubjectIDInjection.csv and SubjectIDHandle.csv) are also read as well for each subject using the subject folder list.
- Template file path: '/location on computer/cohort folder/subject folders/bonsai outputs’
  - Examples:
    - cohort_folder: '/Users/samdhanani/Desktop/Cohort_G’
    - csv_file_path: '/Users/samdhanani/Desktop/Cohort_G/218_1/218_1.csv'
    - handle_file_path: '/Users/samdhanani/Desktop/Cohort_G/218_1/218_1Handle.csv'
- A new folder called “transformed files’ is created for the changes made to the bonsai output csv files. The original files will remain untouched in the subject folder.
- The variables x and sampling_rate_hz are also set in this portion of the code where x is the number of minutes you want to pull out before and after the injection timestamps. The variable sampling_rate_hz is the frame rate the data was recorded in. 

**SubjectID_photobleach_removed.csv**

- This code takes the timestamp from SubjectIDStart.csv and filters out rows in the SubjectID.csv with a timestamp smaller than the start timestamp. This is all based on the computer timestamp, not the system time stamp.
- It then saves this cropped data frame to a new data frame and then saves the data to a new csv file.
SubjectID_photobleach_handle_removed.csv
- First, the start and end timestamps of the handling data are extracted to an empty list called “exclusion_ranges”. This is done using a for loop that goes through each row in the handle data frame and stores the timestamps as start and end tuples in exclusion_ranges. In the handle data frame, the first row becomes the start time and the second becomes the end time and so on until there are no more rows.
- Next, the list of exclusion ranges is used to filter the photobleach_handle_removed data frame where a for loop goes through the list. The for loop filters the data frame by keeping rows with a computer timestamp less than the start time and greater than the end time and then checks again for another tuple in the list exclusion ranges.
- Finally, the last filtering step removes instances of consecutive led states and this affects data processing downstream. A for loop goes through the photobleach_handle_removed data frame and checks for consecutive led states by checking if two rows next to each other have an equal value in the led state column. If there are two consecutive led states of “1” then the first row is removed. If there are two consecutive led states of “2” then the second row is removed.
- An arbitrary x axis is created for the reference led state and the signal led state to plot the datapoints as the removal of the handling data creates gaps of data on the x axis.

**SubjectID_all_baseline.csv**, **SubjectID_all_amph.csv**, **SubjectID_all_full_session.csv**

- This code creates the csv files above from the photobleach_removed_handle_df data (not interpolated). The code begins by reading the injection csv file and using the start and end time of the injection period to determine the pre-injection and post-injection data.
- The first timestamp in the injection csv file is used to determine the end of the pre-injection baseline period and the second timestamp in the injection csv file is used to determine the start of the post injection amph period which lasts until the end of the recording.
- The full session data is made up of datapoints before and after the injection start and end times, in other words the injection time is removed from the data.

**SubjectID_Xmin_baseline.csv**, **SubjectID_Xmin_amph.csv**, **SubjectID_all_full_session.csv**

- The code starts by calculating how many rows to pull out before and after the injection time stamps based on the time the user wants and the frame rate.
- The variable num_rows_interval determines how many rows are going to be pulled out based on the rows_per_min equation and the user defined time defined as ‘x’.
- This is done for the pre and post injection times where the last row of the baseline data frame is identified and the variable num_rows_interval is subtracted from that.
- In the amph data frame the first row is identified and the variable num_rows_interval is added to that.
- Then the interval_pre_injection_df and interval_post_injection_df are combined to make the full_session_df.

**SubjectID_time_subtracted_values_amph.csv**

- This code is for quality control. It calculates how much time is being removed during the post_injection time period by summing up all the time differences greater than the injection end time stamp in column ‘Item2’ in the SubjectIDHandle.csv. 
Calculating the dFF values
Harris lab script

Peak Analysis

