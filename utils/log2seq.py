import os
import random
from datetime import datetime

import numpy as np
import pandas as pd


def is_prime(x):
    for i in range(2, int(x ** 0.5) + 1):
        if x % i == 0:
            return False
    return True


####WORKING METHOD###
# def csv2log_id_sep(filename, caseids_col, acts_col, num, starttime, isplg=False):
#     df = pd.read_csv(filename, sep=';', na_filter=False)
#     if isplg:
#         for id in df[caseids_col]:
#             df[caseids_col] = int(id[9:])
#
#     caseids = df[caseids_col].values
#     ucaseids = pd.unique(caseids)
#
#     case_dict = dict(zip(range(0, ucaseids.size), ucaseids))
#     acts = df[acts_col].values
#
#     act2id = {}
#     i = 1
#     for act in acts:
#         if act not in act2id:
#             act2id[act] = i
#             i += 1
#
#     act_dict = dict((v, k) for k, v in act2id.items())
#     traces = []
#     trace_list = []
#
#     for case in ucaseids:
#         df_case = df.loc[df[caseids_col] == case]
#         df_case = df_case.reset_index(drop=True)
#         acts_case = df_case[acts_col]
#         case_acts = acts_case
#         case_acts_list = case_acts.tolist()
#         trace_list.append(case_acts_list)
#         case_acts = np.asarray([act2id[act] for act in case_acts],
#                                  dtype='int64')
#         traces.append(case_acts)
#
#     length_dist = {}
#     for trace in traces:
#         if len(trace) not in length_dist:
#             length_dist[len(trace)] = 1
#         else:
#             length_dist[len(trace)] += 1
#     act_freq_dist = {}
#
#     for trace in traces:
#         for act in trace:
#             if act not in act_freq_dist:
#                 act_freq_dist[act] = 1
#             else:
#                 act_freq_dist[act] += 1
#     return traces, case_dict, act_dict, length_dist, act_freq_dist


def csv2log_id_sep(filename, caseids_col, acts_col, num, starttime, label_col='label', isplg=False):
    df = pd.read_csv(filename, sep=';', na_filter=False)

    if isplg:
        for id in df[caseids_col]:
            df[caseids_col] = int(id[9:])

    caseids = df[caseids_col].values
    ucaseids = pd.unique(caseids)

    case_dict = dict(zip(range(0, ucaseids.size), ucaseids))
    acts = df[acts_col].values

    act2id = {}
    i = 1
    for act in acts:
        if act not in act2id:
            act2id[act] = i
            i += 1

    act_dict = dict((v, k) for k, v in act2id.items())
    traces = []
    trace_list = []
    labels = []  # List to store labels for each trace

    for case in ucaseids:
        df_case = df.loc[df[caseids_col] == case]
        df_case = df_case.reset_index(drop=True)
        acts_case = df_case[acts_col]
        case_acts = acts_case.tolist()
        trace_list.append(case_acts)

        case_acts = np.asarray([act2id[act] for act in case_acts], dtype='int64')
        traces.append(case_acts)

        # Get the label for this trace (1 for 'deviant', 0 for 'regular')
        label = df_case[label_col].iloc[0]
        if label == 'deviant':
            labels.append(1)
        elif label == 'regular':
            labels.append(0)
        else:
            raise ValueError(f"Unexpected label '{label}' found in case {case}")

    length_dist = {}
    for trace in traces:
        if len(trace) not in length_dist:
            length_dist[len(trace)] = 1
        else:
            length_dist[len(trace)] += 1

    act_freq_dist = {}
    for trace in traces:
        for act in trace:
            if act not in act_freq_dist:
                act_freq_dist[act] = 1
            else:
                act_freq_dist[act] += 1

    return traces, case_dict, act_dict, length_dist, act_freq_dist, labels


def csv2log_id(filename, caseids_col, acts_col, num, starttime, isplg=False):
    df = pd.read_csv(filename, na_filter=False)
    if isplg:
        for id in df[caseids_col]:
            df[caseids_col] = int(id[9:])

    caseids = df[caseids_col].values
    ucaseids = pd.unique(caseids)
    case_dict = dict(zip(range(0, ucaseids.size), ucaseids))
    acts = df[acts_col].values

    act2id = {}
    i = 1
    for act in acts:
        if act not in act2id:
            act2id[act] = i
            i += 1

    PRIME_FLAG = 0
    if is_prime(len(act2id) + 1):
        PRIME_FLAG = 1
        act2id = {}
        act2id['START_TOKEN'] = 1
        i = 2
        for act in acts:
            if act not in act2id:
                act2id[act] = i
                i += 1

    act_dict = dict((v, k) for k, v in act2id.items())
    traces = []
    trace_list = []

    for case in ucaseids:
        df_case = df.loc[df[caseids_col] == case]
        df_case = df_case.reset_index(drop=True)

        if ':' in df_case[starttime]:
            df_case[starttime] = df_case[starttime].apply(time_to_seconds)
        else:
            df_case[starttime] = df_case[starttime].astype(float)

        df_case = df_case.sort_values(by=[starttime])
        df_case = df_case.reset_index(drop=True)
        acts_case = df_case[acts_col]
        case_acts = acts_case
        case_acts_list = case_acts.tolist()

        trace_list.append(case_acts_list)
        if PRIME_FLAG:
            case_acts = np.insert(case_acts, 0, 'START_TOKEN')
        case_acts = np.asarray([act2id[act] for act in case_acts],
                               dtype='int64')
        traces.append(case_acts)
        if len(traces) == num:
            break

    length_dist = {}
    for trace in traces:
        if len(trace) not in length_dist:
            length_dist[len(trace)] = 1
        else:
            length_dist[len(trace)] += 1
    act_freq_dist = {}

    for trace in traces:
        for act in trace:
            if act not in act_freq_dist:
                act_freq_dist[act] = 1
            else:
                act_freq_dist[act] += 1
    # return
    return traces, case_dict, act_dict, length_dist, act_freq_dist


def time_to_seconds2(t):
    minutes, seconds = map(int, t.split(':'))
    return minutes * 60 + seconds


def compute_datetime_dif(time_str1, time_str2):
    dt1 = datetime.strptime(time_str1, "%Y-%m-%d %H:%M:%S.%f")
    dt2 = datetime.strptime(time_str2, "%Y-%m-%d %H:%M:%S.%f")
    delta = dt2 - dt1
    hours_difference = delta.days * 24 + delta.seconds / 3600
    return hours_difference


def time_to_seconds(t):
    # print(t)
    hours, minutes, seconds, _ = map(int, t.split(':'))
    return hours * 3600 + minutes * 60 + seconds


# def model(fname, foldername, data_res, num, caseID, activity, starttime):
#     log = csv2log_id_sep(filename=fname,
#                   caseids_col=caseID,
#                   acts_col=activity,
#                   num=num,
#                   starttime=starttime,
#                   )
#     (traces, case_dict, act_dict,length_dist, act_freq_dist) = log
#     save_path = foldername + '/'
#     os.makedirs(os.path.dirname(save_path), exist_ok=True)
#
#     for trace in traces:
#         trace_list = trace.tolist()
#         path = save_path+'SEP.txt'
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         with open(path, 'a') as f:
#             for item in trace_list:
#                 f.write("%s " % item)
#             f.write("\n")
#
#     csv_file = foldername + "/act_dict.csv"
#     with open(csv_file, 'w') as f:
#         for key in act_dict.keys():
#             f.write("%s,%s\n" % (act_dict[key], key))
#
#     csv_file = foldername + "/act_freq_dict.csv"
#     with open(csv_file, 'w') as f:
#
#         for key in act_freq_dist.keys():
#             f.write("%s,%s\n" % (key, act_freq_dist[key]))
#
#     csv_file = foldername + "/length_dict.csv"
#     with open(csv_file, 'w') as f:
#         maxlen = max(length_dist, key=int)
#         lengths = length_dist.values()
#         seq_num = sum(lengths)
#         for key in length_dist.keys():
#             f.write("%s, %s\n" % (key, length_dist[key]))
#         f.write("max len, %s\n" % (maxlen))
#         f.write("num seq, %s\n" % (seq_num))


def model(fname, foldername, data, data_res, num, caseID, activity, starttime):
    log = csv2log_id_sep(filename=fname,
                         caseids_col=caseID,
                         acts_col=activity,
                         num=num,
                         starttime=starttime,
                         )
    (traces, case_dict, act_dict, length_dist, act_freq_dist, labels) = log
    save_path = foldername + '/'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for trace in traces:
        trace_list = trace.tolist()
        path = save_path + data + ".txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a') as f:
            for item in trace_list:
                f.write("%s " % item)
            f.write("\n")

    # Write labels to a text file
    # labels_file = os.path.join(save_path, data + "_time_duration_norm.txt")
    # with open(labels_file, 'w') as f:
    #     for label in labels:
    #         f.write(f"{label}\n")

    os.makedirs(data_res, exist_ok=True)

    csv_file = os.path.join(data_res, "act_dict.csv")
    with open(csv_file, 'w') as f:
        for key in act_dict.keys():
            f.write("%s,%s\n" % (act_dict[key], key))

    csv_file = os.path.join(data_res, "act_freq_dict.csv")
    with open(csv_file, 'w') as f:
        for key in act_freq_dist.keys():
            f.write("%s,%s\n" % (key, act_freq_dist[key]))

    csv_file = os.path.join(data_res, "length_dict.csv")
    with open(csv_file, 'w') as f:
        maxlen = max(length_dist, key=int)
        lengths = length_dist.values()
        seq_num = sum(lengths)
        for key in length_dist.keys():
            f.write("%s, %s\n" % (key, length_dist[key]))
        f.write("max len, %s\n" % (maxlen))
        f.write("num seq, %s\n" % (seq_num))


def seq2log(dic_file, seq_file, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df = pd.read_csv(dic_file, na_filter=False, header=None)
    f = open(seq_file)
    all_seq = []
    for line in f:
        line = line.split()
        seq = []
        for ind in line:
            seq.append(int(ind))
        all_seq.append(seq)
    act_seq = []
    id_seq = []
    for seq in range(len(all_seq)):
        if len(all_seq[seq]) == 0:
            act_seq.append('Empty')
            id_seq.append(seq)
            continue

        for act in all_seq[seq]:
            act_seq.append(df[0][act - 1])
            id_seq.append(seq)

    df_log = pd.DataFrame()
    df_log['id'] = id_seq
    df_log['act'] = act_seq
    df_log.to_csv(save_path, index=None)


def split(path, save_train_path, save_test_path, save_val_path, train_size, test_size, val_size):
    random.seed(88)
    f = open(path)
    save_train = open(save_train_path, "a")
    save_test = open(save_test_path, 'a')
    save_val = open(save_val_path, 'a')
    lines = f.readlines()
    ids = random.sample(range(0, train_size + test_size + val_size), k=train_size + test_size + val_size)
    for i in range(0, train_size):
        save_train.write(lines[ids[i]])
    for i in range(train_size, train_size + val_size):
        save_val.write(lines[ids[i]])
    for i in range(train_size + val_size, train_size + test_size + val_size):
        save_test.write(lines[ids[i]])

# MAIN
# if __name__ == '__main__':
#     fname = "/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_raw/Sepsis Cases - Event Log.csv"
#     data = 'SEP2'
#     foldername = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_time/' + data + '/data_seq'
#     data_res = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_info/' + data
#     num = 900
#     caseID = "Case ID"
#     activity = "Activity"
#     starttime = "Complete Timestamp"
#
#     model(fname, foldername, data_res, num, caseID, activity, starttime)
