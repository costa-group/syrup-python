from encoding_utils import *

# Aditional contraints

def each_function_is_used(b0, initial_idx, end_idx):
    print("; All uninterpreted functions are eventually used")
    for i in range(initial_idx, end_idx):
        or_variables = []
        for j in range(b0):
            or_variables.append(add_eq(t(j), i))
        print(add_assert(add_or(*or_variables)))
