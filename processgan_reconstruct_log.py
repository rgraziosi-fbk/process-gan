import numpy as np
import pandas as pd
import pm4py
import datetime
import copy

ACTIVITY_FILE = '300_result_trans.txt'
TIMESTAMP_FILE = '300_result_trans_time.txt'

# The timestamp from which to start generating new traces (could be the first timestamp of test set, or the last timestamp of train set)
START_TIMESTAMP = datetime.datetime.strptime('26.10.2014 20:21:00', '%d.%m.%Y %H:%M:%S')

OUTPUT_FILENAME = 'gen'
CSV_SEP = ';'
GEN_LOG_SIZE = 157

CASE_KEY = 'case:concept:name'
ACTIVITY_KEY = 'concept:name'
TIMESTAMP_KEY = 'time:timestamp'


# Read the CSV file into a DataFrame
df = pd.read_csv('act_dict.csv', header=None, names=['activity_name', 'activity_idx'])

# Convert the DataFrame to a dictionary
activity_dict = df.set_index('activity_name')['activity_idx'].to_dict()
activity_dict_inv = { i: a for a, i in activity_dict.items() }


# Read the activities file
activities = []
with open(ACTIVITY_FILE, 'r') as file:
  for line in file:
    if line == '\n': continue
    
    activities.append([])
    current_idx = len(activities) - 1

    numbers = line.strip().split()
    
    for number in numbers:
      activity = activity_dict_inv.get(int(number), 'Unknown')
      activities[current_idx].append(activity)


# Read the timestamps file
timestamps = []
with open(TIMESTAMP_FILE, 'r') as file:
  for line in file:
    if line == '\n': continue
    
    timestamps.append([])
    current_idx = len(timestamps) - 1

    ts = line.strip().split()
    ts = [float(ts_i) for ts_i in ts] # convert to floats
    normalization_factor = ts[-1] # last value is the normalization factor used to normalize timestamps
    ts = ts[:-1]
    ts = [ts_i*normalization_factor for ts_i in ts] # de-normalize timestamps
    ts = [ts_i*60*60 for ts_i in ts] # convert from hours to seconds

    timestamps[current_idx].extend(ts)


rows = []
for case_id, (activities_i, timestamps_i) in enumerate(zip(activities, timestamps), start=1):
  case_id_str = f'GEN_{case_id}'

  assert len(activities_i) == len(timestamps_i)

  current_timestamp = copy.deepcopy(START_TIMESTAMP)

  for i in range(len(activities_i)):
    current_timestamp += datetime.timedelta(seconds=timestamps_i[i])

    rows.append({
      CASE_KEY: case_id_str,
      ACTIVITY_KEY: activities_i[i],
      TIMESTAMP_KEY: datetime.datetime.strftime(current_timestamp, '%Y.%m.%d %H:%M:%S')
    })

# Create a DataFrame from the list of rows
df = pd.DataFrame(rows)

# cast 'case:concept:name' to string and 'time:timestamp' to datetime
df[CASE_KEY] = df[CASE_KEY].astype(str)
df[TIMESTAMP_KEY] = pd.to_datetime(df[TIMESTAMP_KEY])

# Save df to csv and xes
df.to_csv(f'{OUTPUT_FILENAME}.csv', index=False)
log = pm4py.format_dataframe(df, case_id=CASE_KEY, activity_key=ACTIVITY_KEY)
pm4py.write_xes(log, f'{OUTPUT_FILENAME}.xes')


# Split the log into splits of size GEN_LOG_SIZE
# If there are leftover cases, discard them
# If there are not enough cases, raise error

# get case names
case_names = df[CASE_KEY].unique()
#shuffle
np.random.shuffle(case_names)

# split
splits = []
for i in range(0, len(case_names), GEN_LOG_SIZE):
  split = case_names[i:i+GEN_LOG_SIZE]
  splits.append(split)

# check if there are leftover cases
if len(splits[-1]) < GEN_LOG_SIZE:
  print('Discarding leftover cases')
  splits = splits[:-1]

# check if there are not enough cases
if len(splits[0]) < GEN_LOG_SIZE:
  raise ValueError('Not enough cases to generate a split')

# save splits
for i, split in enumerate(splits):
  split_df = df[df[CASE_KEY].isin(split)]
  split_df.to_csv(f'{OUTPUT_FILENAME}_{i}.csv', index=False, sep=CSV_SEP)
  split_log = pm4py.format_dataframe(split_df, case_id=CASE_KEY, activity_key=ACTIVITY_KEY)
  pm4py.write_xes(split_log, f'{OUTPUT_FILENAME}_{i}.xes')