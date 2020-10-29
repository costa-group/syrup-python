import sys
import pathlib

costabs_path = "/tmp/costabs/"
encoding_name = "encoding_Z3.smt2"
tmp_path = "/tmp/"

encoding_stream = sys.stdout

def initialize_dir_and_streams():
    global encoding_stream
    pathlib.Path(costabs_path).mkdir(parents=True, exist_ok=True)
    encoding_stream = open(costabs_path + encoding_name, 'w')

def write_encoding(string):
    print(string, file=encoding_stream)