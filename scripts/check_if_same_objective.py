#!/usr/bin/python3
# Script to check if the two encodings obtain the same objective. Assume
# we have a dir, in which each file contains the result from analyzing both Z3 encodings
# and (get-objective) statement has been added.

import re
import glob

dir = "../experiments/comparison"
log = "../experiments/comparison_log.txt"
results = "../experiments/comparison_results.txt"

version1 = "Ocaml"
version2 = "Python"

results_stream = open(results, 'w')
log_stream = open(log, 'w')

first_number_left = 0
first_number_right = 0

second_number_left = 0
second_number_right = 0

optimal_equal = 0
optimal_syrup = 0
optimal_python = 0

optimal_syrup_non_optimal_python = 0
optimal_python_non_optimal_syrup = 0
non_optimal = 0

total = 0

def analyze_cases(file_name):
    global optimal_equal, optimal_syrup, optimal_python, optimal_python_non_optimal_syrup, \
        optimal_syrup_non_optimal_python, non_optimal, total
    total += 1
    syrup_equal = first_number_left == first_number_right
    python_equal = second_number_left == second_number_right
    if syrup_equal and python_equal:
        if first_number_left == second_number_left:
            optimal_equal += 1
            print("Analyzing " + file_name + ": Optimal and same gas associated!", file=log_stream)
        elif first_number_left < second_number_left:
            optimal_syrup += 1
            print("Analyzing " + file_name + ": " + version1 + " optimal gas lower than" + version2 + "...", file=log_stream)
        else:
            optimal_python += 1
            print("Analyzing " + file_name + ": " + version2 + " optimal gas lower than" + version1 + "...", file=log_stream)
    else:
        if syrup_equal:
            optimal_syrup_non_optimal_python += 1
            print("Analyzing " + file_name + ": " + version1 + " found optimal, " + version2 + " wasn't!", file=log_stream)
        elif python_equal:
            optimal_python_non_optimal_syrup += 1
            print("Analyzing " + file_name + ": " + version2 + " found optimal, " + version2 + " wasn't!", file=log_stream)
        else:
            non_optimal += 1
            print("Analyzing " + file_name + ": Neither " + version1 + " nor " + version2 + " were found optimal", file=log_stream)


def submatch(string, first):
    global first_number_left, first_number_right, second_number_left, second_number_right
    subpattern = re.compile("\(interval (.*) (.*)\)")
    for submatch in re.finditer(subpattern, string):
        if first:
            first_number_left = int(submatch.group(1))
            first_number_right = int(submatch.group(2))
        else:
            second_number_left = int(submatch.group(1))
            second_number_right = int(submatch.group(2))
        return True
    return False


def analyze_file(filename):
    global first_number_left, first_number_right, second_number_left, second_number_right
    first = True
    for line in open(filename, 'r'):
        for match in re.finditer(pattern, line):
            if submatch(match.group(1), first):
                if first:
                    first = False
                continue
            if first:
                first_number_left = int(match.group(1))
                first_number_right = first_number_left
                first = False
            else:
                second_number_left = int(match.group(1))
                second_number_right = second_number_left


if __name__=="__main__":
    pattern = re.compile("\(gas (.*)\)")
    ok = 0
    error = 0
    for file in glob.glob(dir + "/*.txt"):
        analyze_file(file)
        analyze_cases(file.split("/")[-1])

    print("We have analyzed a total of " + str(total) + " files, where:", file=results_stream)
    print("-" + str(optimal_equal) + " were proven optimal for both versions", file=results_stream)
    print("-" + str(optimal_syrup) + " were proven optimal for both versions, but " + version1 + " cost was lower", file=results_stream)
    print("-" + str(optimal_python) + " were proven optimal for both versions, but " + version2 + " cost was lower", file=results_stream)
    print("-" + str(optimal_syrup_non_optimal_python) + " were proven optimal for " + version1 + ", but nor for " + version2, file=results_stream)
    print("-" + str(optimal_python_non_optimal_syrup) + " were proven optimal for " + version2 + ", but nor for " + version1, file=results_stream)
    print("-" + str(non_optimal) + " weren't proven optimal for both versions", file=results_stream)

    results_stream.close()
    log_stream.close()