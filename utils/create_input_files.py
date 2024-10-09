import argparse
import os
from log2seq import model
from timestamp_process import process_timestamp_sep


def main():
    parser = argparse.ArgumentParser(description='Process data with log2seq model and timestamp processing.')

    parser.add_argument('--data', type=str, required=True, help='Name of the dataset (e.g., sepsis)')
    parser.add_argument('--num', type=int, required=True, help='Number of cases (not used!)')
    parser.add_argument('--caseID', type=str, required=True, help='Column name for case IDs')
    parser.add_argument('--activity', type=str, required=True, help='Column name for activities')
    parser.add_argument('--starttime', type=str, required=True, help='Column name for timestamp')

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.abspath(os.path.join(script_dir, '..'))

    # Set up relative paths using base_path
    fname = os.path.join(base_path, "data", "data_raw", args.data + ".csv")
    foldername = os.path.join(base_path, "data", "data_time", args.data, "data_seq")
    data_res = os.path.join(base_path, "data", "data_info", args.data)
    save_file = os.path.join(base_path, "data", "data_time", args.data, "data_seq", args.data + '_time_dif_norm.txt')
    save_file2 = os.path.join(base_path, "data", "data_time", args.data, "data_seq",
                              args.data + '_time_duration_norm.txt')

    # Run the model and timestamp process
    model(fname, foldername, args.data, data_res, args.num, args.caseID, args.activity, args.starttime)
    process_timestamp_sep(fname, save_file, save_file2, args.caseID, args.starttime)


if __name__ == '__main__':
    main()

# if __name__ == '__main__':
#     data = 'SEPSIS_FBK'
#     fname = "/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_raw/" + data + ".csv"
#
#     foldername = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_time/' + data + '/data_seq'
#     data_res = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_info/' + data
#
#     save_file = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_time/' + data + '/data_seq/' + data + '_time_dif_norm.txt'
#     save_file2 = '/Users/francescofolino/PycharmProjects/ProcessGAN-main/data/data_time/' + data + '/data_seq/' + data + '_time_duration_norm.txt'
#
#     num = 782
#     caseID = "Case ID"
#     activity = "Activity"
#     starttime = "time:timestamp"
#
#     model(fname, foldername, data, data_res, num, caseID, activity, starttime)
#
#     process_timestamp_sep(fname, save_file, save_file2, caseID, starttime)
