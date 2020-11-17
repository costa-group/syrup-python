#!/usr/bin/python3
# Script to filter blocks by using the generated csv

import pandas as pd

csv_path = "/home/alejandro/repos/syrup-python/opti-eval-cav/most-called-contracts/results_Z3.csv"
results_path = "../scripts/examples.txt"
number_of_analyzed = 30

if __name__ == "__main__":
    contracts_z3 = pd.read_csv(csv_path)
    interesting_contracts = contracts_z3[contracts_z3['shown_optimal']]
    interesting_contracts = interesting_contracts.sort_values('source_gas_cost')
    step = interesting_contracts.shape[0] // number_of_analyzed
    result_file = open(results_path, 'w')
    for i in range(number_of_analyzed-1):
        print(interesting_contracts.iloc[step*i]['block_id'].split('/')[-1], file=result_file)


