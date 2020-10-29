from encoding_utils import *
from encoding_files import write_encoding

# Aditional contraints

# Each uninterpreted function is used at least once
def each_function_is_used_at_least_once(b0, initial_idx, end_idx):
    write_encoding("; All uninterpreted functions are eventually used")
    for i in range(initial_idx, end_idx):
        or_variables = []
        for j in range(b0):
            or_variables.append(add_eq(t(j), i))
        write_encoding(add_assert(add_or(*or_variables)))


# Each uninterpreted function is used at most once. This means that
# if we assign a instruction to tj, then we cannot assign the same
# function for any other ti.
def each_function_is_used_at_most_once(b0, initial_idx, end_idx):
    write_encoding("; All interpreted functions can be used at most once")
    for j in range(b0):
        remaining_instr = set(range(b0))
        remaining_instr.remove(j)
        for instr in range(initial_idx, end_idx):
            write_encoding(add_assert(add_implies(add_eq(t(j), instr),
                                         add_and(*list(map(lambda i: add_not(add_eq(t(i), instr)), remaining_instr))))))


# We combine both constraints: each instruction is used at least once and at most once.
def each_function_is_used_exactly_once(b0, initial_idx, end_idx):
    write_encoding("; All interpreted functions are used exactly once (at most once + at least once)")
    each_function_is_used_at_least_once(b0, initial_idx, end_idx)
    each_function_is_used_at_most_once(b0, initial_idx, end_idx)


# Only a pop can be performed if no instruction introducing a value in the stack was performed just before.
# At this point, this means only pop and swap instructions are valid before a pop.
def no_output_before_pop(b0, theta_stack):
    write_encoding("; If we push or dup a value, the following instruction cannot be a pop")
    theta_nop = theta_stack["NOP"]
    theta_push = theta_stack["PUSH"]
    theta_swaps = [v for k,v in theta_stack.items() if k.startswith('SWAP')]
    no_output_instr_theta = [theta_push, *theta_swaps]
    for j in range(b0-1):
        write_encoding(add_assert(add_implies(add_eq(t(j+1), theta_nop),
                         add_or(*list(map(lambda instr: add_eq(t(j), instr), no_output_instr_theta))))))


# If we choose swap as an instruction, then it cannot swap the same two elements.
def swap_same_element(b0, bk, theta_stack):
    pass


# As we assume that each value that appears in the ops is needed, then we need to
# push each value at least once.
def push_each_element_at_least_once(b0, theta_push, pushed_elements):
    write_encoding("; All values are eventually pushed")
    for i in pushed_elements:
        or_variables = []
        for j in range(b0):
            or_variables.append(add_and(add_eq(t(j), theta_push), add_eq(a(j), i)))
        write_encoding(add_assert(add_or(*or_variables)))


# We can generate a graph that represents the dependencies between different opcodes
# (input). Then, we can assume that each one has to follow that restriction.
def restrain_instruction_order():
    pass
