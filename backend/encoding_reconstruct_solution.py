from encoding_utils import *
from encoding_files import write_encoding


# Given a dict that contains info from the sequence, transforms it into
# their corresponding constraints. This dict if of the form {k : [tj, aj]},
# where k indicates the position in the sequence, tj the assigned theta value and
# aj the pushed value. If tj != theta(PUSH), then aj = -1
def generate_encoding_from_log_json_dict(sequence_dict, initial_idx=0):
    for pos, values in sequence_dict.items():
        # If it's a tuple, then it is a push and we need to generate the correspondent constraint for aj.
        if type(values) == list:
            theta, aj = values[0], values[1]
            write_encoding(add_assert(add_eq(a(int(pos) + initial_idx), aj)))
        else:
            theta = values
        write_encoding(add_assert(add_eq(t(int(pos)+initial_idx), theta)))
