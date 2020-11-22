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
        remaining_pos = set(range(b0))
        remaining_pos.remove(j)
        for instr in range(initial_idx, end_idx):
            write_encoding(add_assert(add_implies(add_eq(t(j), instr),
                                         add_and(*list(map(lambda i: add_not(add_eq(t(i), instr)), remaining_pos))))))


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
def restrain_instruction_order(b0, depencency_graph, first_time_instruction_appears, theta):
    write_encoding("; Constraints that reflect the order among instructions")
    for instr, previous_instrs in depencency_graph.items():
        previous_values = []
        for previous_instr_name, aj in previous_instrs:
            # We add a clause for each possible position in which previous equation may appear
            for previous_position in range(first_time_instruction_appears[previous_instr_name],
                                           first_time_instruction_appears[instr]):
                # If aj == -1, then we don't need to consider to assign aj
                if aj == -1:
                    previous_values.append(add_eq(t(previous_position), theta[previous_instr_name]))
                else:
                    previous_values.append(add_and(add_eq(t(previous_position), theta[previous_instr_name]),
                                                   add_eq(a(previous_position), aj)))
        for position in range(first_time_instruction_appears[instr], b0):
            write_encoding(add_assert(add_implies(add_eq(t(position), theta[instr]), add_or(*previous_values))))
            # We update previous values list to add the possibility that previous instructions could be
            # executed in current position
            for previous_instr_name, aj in previous_instrs:
                # If aj == -1, then we don't need to consider to assign aj
                if aj == -1:
                    previous_values.append(add_eq(t(position), theta[previous_instr_name]))
                else:
                    previous_values.append(add_and(add_eq(t(position), theta[previous_instr_name]),
                                                   add_eq(a(position), aj)))


# Each uninterpreted function is used at least once, but we take into account first position it may appear
def each_function_is_used_at_least_one_with_position(b0, user_instr, first_time_instruction_appears, theta_dict):
    write_encoding("; All uninterpreted functions are eventually used, and only in some positions")
    for instr in user_instr:
        id = instr['id']
        theta_instr = theta_dict[id]
        first_possible_ocurrence = first_time_instruction_appears[id]
        # For each position in which the instruction cannot appear, we add an explicit statement
        for j in range(first_possible_ocurrence):
            write_encoding(add_assert(add_not(add_eq(t(j), theta_instr))))
        
        # We add a statement with the remaining positions to state that the instruction must appear
        # at least one
        or_variables = []
        for j in range(first_possible_ocurrence, b0):
            or_variables.append(add_eq(t(j), theta_instr))
        write_encoding(add_assert(add_or(*or_variables)))