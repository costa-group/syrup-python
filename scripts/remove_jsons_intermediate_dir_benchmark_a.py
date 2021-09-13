#!/usr/bin/env python3

import glob 
import os
import shutil

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
directory = project_path + "/results-a/SFS_OK"

if __name__ == "__main__":
    for contract_path in [f.path for f in os.scandir(directory) if f.is_dir()]:
        shutil.rmtree(contract_path + '/disasms')
        for regular_file in [f.path for f in os.scandir(contract_path) if f.is_file()]:
            os.remove(regular_file)
        for file in glob.glob(contract_path + "/**/*.json"):
            new_path = contract_path + "/" + file.split("/")[-1]
            os.rename(file, new_path)
        os.rmdir(contract_path + "/jsons")
