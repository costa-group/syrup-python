# Methods containing the generation of constraints
# for applying superoptimization. It is assumed the
# SFS has already been generated

from encoding_utils import *
from encoding_initialize import initialize_variables, variables_assignment_constraint, \
    initial_stack_encoding, final_stack_encoding
from encoding_cost import paper_soft_constraints
from encoding_instructions import instructions_constraints
from encoding_redundant import *
from encoding_files import write_encoding, write_opcode_map, write_instruction_map


# Method to generate redundant constraints according to flags (at least once is included by default)
def generate_redundant_constraints(flags, b0, user_instr, theta_stack, theta_comm, theta_non_comm, final_stack):
    pushed_values = generate_phi_dict(user_instr, final_stack)
    if flags['at-most']:
        each_function_is_used_at_most_once(b0, len(theta_stack), len(theta_stack) + len(theta_comm) + len(theta_non_comm))
    if flags['pushed-at-least']:
        push_each_element_at_least_once(b0, theta_stack['PUSH'], pushed_values)


# Method to generate optional asserts according to additional info
def generate_asserts_from_additional_info(additional_info):
    if additional_info['tout'] is not None:
        write_encoding(set_timeout(additional_info['tout']))


# Method to generate complete representation
def generate_smtlib_encoding(b0, bs, usr_instr, variables, initial_stack, final_stack, flags, additional_info):
    write_encoding(set_logic('QF_LIA'))
    generate_asserts_from_additional_info(additional_info)
    initialize_variables(variables, bs, b0)
    variables_assignment_constraint(variables)
    theta_stack = generate_stack_theta(bs)
    theta_comm, theta_non_comm = generate_uninterpreted_theta(usr_instr, len(theta_stack))
    comm_instr, non_comm_instr = separe_usr_instr(usr_instr)
    instructions_constraints(b0, bs, comm_instr, non_comm_instr, theta_stack, theta_comm, theta_non_comm)
    initial_stack_encoding(initial_stack, bs)
    final_stack_encoding(final_stack, bs, b0)
    each_function_is_used_at_least_once(b0, len(theta_stack), len(theta_stack) + len(theta_comm) + len(theta_non_comm))
    generate_redundant_constraints(flags, b0, usr_instr, theta_stack, theta_comm, theta_non_comm, final_stack)
    paper_soft_constraints(b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm)
    write_encoding(check_sat())
    write_encoding(get_objectives())
    # get_model()
    for j in range(b0):
        write_encoding(get_value(t(j)))
        write_encoding(get_value(a(j)))
    write_encoding("; Stack: " + str(theta_stack))
    write_encoding("; Comm: " + str(theta_comm))
    write_encoding("; Non-Comm: " + str(theta_non_comm))

    theta_dict = dict(theta_stack, **theta_comm, **theta_non_comm)

    write_instruction_map(generate_instr_map(usr_instr, theta_stack, theta_comm, theta_non_comm))
    write_opcode_map(generate_disasm_map(usr_instr, theta_dict))
