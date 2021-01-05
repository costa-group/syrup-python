# Methods containing the generation of constraints
# for applying superoptimization. It is assumed the
# SFS has already been generated

from encoding_utils import *
from encoding_initialize import initialize_variables, variables_assignment_constraint, \
    initial_stack_encoding, final_stack_encoding
from encoding_cost import paper_soft_constraints, label_name
from encoding_instructions import instructions_constraints
from encoding_redundant import *
from encoding_files import write_encoding, write_opcode_map, write_instruction_map, write_gas_map


# Method to generate redundant constraints according to flags (at least once is included by default)
def generate_redundant_constraints(flags, b0, user_instr, theta_stack, theta_comm, theta_non_comm, final_stack):
    if flags['at-most']:
        valid_theta = list(map(lambda instr: theta_comm[instr['id']] if instr['commutative'] else theta_non_comm[instr['id']],
                             filter(lambda instr: instr['gas'] > 2, user_instr)))
        each_function_is_used_at_most_once(b0, valid_theta)
    if flags['pushed-at-least']:
        pushed_values = generate_phi_dict(user_instr, final_stack)
        push_each_element_at_least_once(b0, theta_stack['PUSH'], pushed_values)
    if flags['no-output-before-pop']:
        no_output_before_pop(b0, theta_stack)
    if flags['instruction-order']:
        theta_dict = dict(theta_stack, **theta_comm, **theta_non_comm)
        dependency_graph = generate_dependency_graph(user_instr)
        instructions_position = generate_number_of_previous_instr_dict(dependency_graph)
        restrain_instruction_order(b0, dependency_graph, instructions_position, theta_dict)
        each_function_is_used_at_least_one_with_position(b0, user_instr, instructions_position, theta_dict)
    # If flag isn't set, then we use by default the generation for each function used at least once in each position
    else:
        each_function_is_used_at_least_once(b0, len(theta_stack),
                                            len(theta_stack) + len(theta_comm) + len(theta_non_comm))


# Method to generate optional asserts according to additional info. It includes that info that relies on the
# specific solver
def generate_asserts_from_additional_info(additional_info):
    if additional_info['tout'] is not None:
        if additional_info['solver'] == "z3":
            write_encoding(set_timeout(1000 * additional_info['tout']))
        elif additional_info['solver'] == "oms":
            write_encoding(set_timeout(float(additional_info['tout'])))


def generate_soft_constraints(solver_name, b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm):
    if solver_name == "z3" or solver_name == "oms":
        paper_soft_constraints(b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm)
    else:
        paper_soft_constraints(b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm, True)


def generate_cost_functions(solver_name):
    if solver_name == "oms":
        write_encoding(set_minimize_function(label_name))


def generate_configuration_statements(solver_name):
    if solver_name == "oms":
        write_encoding(set_model_true())


# Adding necessary statements after check_sat statement.
# Barcelogic doesn't support (get-objectives) statement.
def generate_final_statements(solver_name):
    if solver_name == "z3":
        write_encoding(get_objectives())
    elif solver_name == "oms":
        write_encoding(get_objectives())
        # If solver is OMS, we allow to generate the model for non-optimal solutions
        write_encoding(load_objective_model())


# Method to generate complete representation
def generate_smtlib_encoding(b0, bs, usr_instr, variables, initial_stack, final_stack, flags, additional_info):
    solver_name = additional_info['solver']
    write_encoding(set_logic('QF_LIA'))
    generate_configuration_statements(solver_name)
    generate_asserts_from_additional_info(additional_info)
    initialize_variables(variables, bs, b0)
    variables_assignment_constraint(variables)
    theta_stack = generate_stack_theta(bs)
    theta_comm, theta_non_comm = generate_uninterpreted_theta(usr_instr, len(theta_stack))
    comm_instr, non_comm_instr = separe_usr_instr(usr_instr)
    instructions_constraints(b0, bs, comm_instr, non_comm_instr, theta_stack, theta_comm, theta_non_comm)
    initial_stack_encoding(initial_stack, bs)
    final_stack_encoding(final_stack, bs, b0)
    generate_redundant_constraints(flags, b0, usr_instr, theta_stack, theta_comm, theta_non_comm, final_stack)
    generate_soft_constraints(solver_name, b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm)
    generate_cost_functions(solver_name)
    write_encoding(check_sat())
    generate_final_statements(solver_name)
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
    write_gas_map(generate_costs_ordered_dict(bs, usr_instr, theta_stack, theta_comm, theta_non_comm))
