# Methods containing the generation of constraints
# for applying superoptimization. It is assumed the
# SFS has already been generated

from encoding_utils import *
from encoding_initialize import initialize_variables, variables_assignment_constraint, \
    initial_stack_encoding, final_stack_encoding
from encoding_cost import paper_soft_constraints
from encoding_instructions import instructions_constraints
from encoding_redundant import each_function_is_used_at_least_once
from encoding_files import write_encoding

# Method to generate complete representation

def generate_smtlib_encoding(b0, bs, usr_instr, variables, initial_stack, final_stack):
    write_encoding(set_logic('QF_LIA'))
    initialize_variables(variables, bs, b0)
    variables_assignment_constraint(variables)
    theta_stack = generate_stack_theta(bs)
    theta_comm, theta_non_comm = generate_uninterpreted_theta(usr_instr, len(theta_stack))
    comm_instr, non_comm_instr = separe_usr_instr(usr_instr)
    instructions_constraints(b0, bs, comm_instr, non_comm_instr, theta_stack, theta_comm, theta_non_comm)
    initial_stack_encoding(initial_stack, bs)
    final_stack_encoding(final_stack, bs, b0)
    each_function_is_used_at_least_once(b0, len(theta_stack), len(theta_stack) + len(theta_comm) + len(theta_non_comm))
    paper_soft_constraints(b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm)
    check_sat()
    get_objectives()
    # get_model()
    for j in range(b0):
        write_encoding(get_value(t(j)))
        write_encoding(get_value(a(j)))
    write_encoding("; Stack: " + str(theta_stack))
    write_encoding("; Comm: " + str(theta_comm))
    write_encoding("; Non-Comm: " + str(theta_non_comm))