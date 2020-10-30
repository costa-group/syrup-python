import sys
import pathlib

costabs_path = "/tmp/costabs/"
encoding_name = "encoding_Z3.smt2"

encoding_stream = sys.stdout

def initialize_dir_and_streams(path_to_store):
    global encoding_stream
    global costabs_path

    # Files will be stored in costabs path, so we create it just in case
    # it doesn't exist.
    if path_to_store[-1] != "/":
        path_to_store += "/"

    costabs_path = path_to_store
    pathlib.Path(costabs_path).mkdir(parents=True, exist_ok=True)
    encoding_stream = open(costabs_path + encoding_name, 'w')

def write_encoding(string):
    print(string, file=encoding_stream)