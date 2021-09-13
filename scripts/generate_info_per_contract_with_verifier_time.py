#!/usr/bin/env python3

import glob 
import os
import pathlib
import pandas as pd
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-block-results-folder", metavar='blocks_directory', action='store', type=str,
                        help="folder that contains the csvs to combine. It must be in the proper format",
                        required=True)
    parser.add_argument("-combined-csvs-folder", metavar='final_directory', action='store', type=str,
                        help="folder that will store the csvs containing the statistics per category", required=True)

    args = parser.parse_args()

    parent_directory = args.block_results_folder
    final_directory = args.combined_csvs_folder

    pathlib.Path(final_directory).mkdir(parents=True, exist_ok=True)

    for encoding_dir in [f.path for f in os.scandir(parent_directory) if f.is_dir()]:
        encoding = encoding_dir.split('/')[-1]
        for directory in [f.path for f in os.scandir(encoding_dir) if f.is_dir()]:
            solver = (directory.split('/')[-1]).split('_')[0]
            timeout = (directory.split('/')[-1]).split('_')[1]
            row_list = []
            for results_csv in glob.glob(directory + "/0x*.csv"):
                csv_row = {}
                csv_row['name'] = (results_csv.split('/')[-1]).split('_')[0]
                df = pd.read_csv(results_csv)
                csv_row['saved_gas'] = df['saved_gas'].sum()
                csv_row['time'] = df['solver_time_in_sec'].sum()
                csv_row['already_optimal'] = df[df['shown_optimal'] & (df['saved_gas'] == 0)].shape[0]
                csv_row['discovered_optimal'] = df[df['shown_optimal'] & (df['saved_gas'] > 0)].shape[0]
                csv_row['non_optimal_with_less_gas'] = df[(df['shown_optimal'] == False) & 
                                                        (df['no_model_found'] == False) & (df['saved_gas'] > 0)].shape[0]
                csv_row['non_optimal_with_same_gas'] = df[(df['shown_optimal'] == False) & 
                                                        (df['no_model_found'] == False) & (df['saved_gas'] == 0)].shape[0]
                csv_row['no_solution_found'] = df[(df['shown_optimal'] == False) & (df['no_model_found'])].shape[0]
                csv_row['verifier_total_time'] = df['verifier_time'].sum()
                csv_row['verifier_number'] = df[df['no_model_found'] == False].shape[0]
                csv_row['all_verified'] = all(df['result_is_correct'].tolist())
                row_list.append(csv_row)
            df = pd.DataFrame(row_list, columns=['name', 'saved_gas', 'time', 'already_optimal', 'discovered_optimal', 
                                                'non_optimal_with_less_gas', 'non_optimal_with_same_gas', 'no_solution_found', 
                                                'verifier_total_time', 'all_verified'])
            pathlib.Path(final_directory + encoding).mkdir(parents=True, exist_ok=True)
            csv_file = final_directory + encoding + "/" + encoding + "_" + solver + ".csv"
            df.to_csv(csv_file)
