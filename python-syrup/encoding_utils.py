# Module that contains parameter declarations and
# other auxiliary methods to generate the encoding

from smtlib_utils import *
from collections import OrderedDict
import re

# We set the maximum k dup and swap instructions
# can have.

max_k_dup = 16
max_k_swap = 16

# Maximum size integers have in the EVM

int_limit = 2**256

# Methods for generating string corresponding to
# variables we will be using for the encoding


def u(i,j):
    return var2str("u", i,j)


def x(i,j):
    return var2str("x", i, j)


def t(i):
    return var2str('t', i)


def a(i):
    return var2str('a', i)

# Auxiliary methods for defining the constraints

def move(j, alpha, beta, delta):
    and_variables = []

    # Move can be empty
    if alpha > beta:
        return "true"
    for i in range(alpha, beta+1):
        first_and = add_eq(u(i+delta, j+1), u(i,j))
        second_and = add_eq(x(i+delta, j+1), x(i,j))
        and_variables.append(add_and(first_and, second_and))
    return add_and(*and_variables)


def generate_stack_theta(bs):
    theta = {"PUSH": 0, "POP": 1, "NOP": 2}
    initial_index = 3
    for i in range(1, min(bs, max_k_dup+1)):
        theta["DUP" + str(i)] = initial_index
        initial_index += 1
    for i in range(1, min(bs, max_k_swap+1)):
        theta["SWAP" + str(i)] = initial_index
        initial_index += 1
    return theta


# Returns two different dictionaries: the first one, for
# commutative functions and the second one for
# non-commutative functions
def generate_uninterpreted_theta(user_instr, initial_index):
    theta_comm = {}
    theta_non_comm = {}
    for instr in user_instr:
        if instr['commutative']:
            theta_comm[instr['id']] = initial_index
        else:
            theta_non_comm[instr['id']] = initial_index
        initial_index += 1
    return theta_comm, theta_non_comm


# Separates user instructions in two groups, according to whether they
# are commutative or not.
def separe_usr_instr(user_instr):
    comm_functions = []
    non_comm_functions = []
    for instr in user_instr:
        if instr['commutative']:
            comm_functions.append(instr)
        else:
            non_comm_functions.append(instr)
    return comm_functions, non_comm_functions


# Generates an ordered dict that contains all instructions associated value of theta
# as keys, and their gas cost as values. Ordered by increasing costs
def generate_costs_ordered_dict(bs, user_instr, theta_stack, theta_comm, theta_non_comm):
    instr_costs = {theta_stack["PUSH"]: 3, theta_stack["POP"]: 2, theta_stack["NOP"]: 0}
    for i in range(1, min(bs, max_k_dup + 1)):
        instr_costs[theta_stack["DUP" + str(i)]] = 3
    for i in range(1, min(bs, max_k_swap + 1)):
        instr_costs[theta_stack["SWAP" + str(i)]] = 3
    for instr in user_instr:
        if instr['commutative']:
            instr_costs[theta_comm[instr['id']]] = instr['gas']
        else:
            instr_costs[theta_non_comm[instr['id']]] = instr['gas']
    return OrderedDict(sorted(instr_costs.items(), key=lambda t: t[1]))


# Generates an ordered dict that has the cost of Wp sets as keys
# and the theta value of opcodes with that cost as values.
# Ordered by increasing costs
def generate_disjoint_sets_from_cost(ordered_costs):
    disjoint_set = {}
    for id in ordered_costs:
        gas_cost = ordered_costs[id]
        if gas_cost in disjoint_set:
            disjoint_set[gas_cost].append(id)
        else:
            disjoint_set[gas_cost] = [id]
    return OrderedDict(sorted(disjoint_set.items(), key=lambda t: t[0]))


def generate_recursive_dependence(elem, user_instr, initial_stack, ):

    # Case base: if an element is already at initial_stack, then we
    # don't need to perform additional instructions to get its value.
    # This could include int values, so it is fundamental that this
    # condition comes before the next one
    if elem in initial_stack:
        return 0

    # Case base: if an element is a number, then it returns 1, as we
    # need to push that element.
    if type(elem) == int:
        return 1

    # Case base: we have already analyzed that value, so there's no
    # change.

    # We search for instruction that contains elem as output
    instruction = list(filter(lambda instr: elem in instr['outpt_sk'], user_instr))[0]
    precedence = 0
    ids = []
    for antecedent in instruction['inpt_sk']:
        generate_recursive_dependence(antecedent, user_instr, initial_stack)


# Generates a list containing graphs that represent the dependencies between
# inputs and outputs from different instructions
def generate_instr_dependencies(user_instr, initial_stack, final_stack, theta):
    evolving = {}

    # Dict that contains theta value of an instruction and the theta value from the
    # instructions before

    theta_before = {}
    # Elements in initial stack are leafs in our graph, and they have
    # no restrictions in appearing from first instruction
    for elem in initial_stack:
        elem += 1

    for elem in final_stack:

        # We are only interested in those variables that have been generated
        # from an uninterpreted function.
        if type(elem) == str and elem not in initial_stack:
            pass


# We generate a dict that given the theta value of an instruction, returns the
# theta values of instructions that must be executed to obtain its input
def generate_dependency_theta_graph(user_instr, theta):
    dependency_theta_graph = {}
    for instr in user_instr:
        theta_id_act = theta[instr['id']]
        dependency_theta_graph[theta_id_act]= set()
        for stack_elem in instr['inpt_sk']:

            # We don't consider ints, as we will explicitely state that
            # all values in instr['inpt_sk] must be eventually pushed

            # We search for another instruction that generates the
            # stack elem as an output and add it to the set
            if type(stack_elem) == str:
                previous_instr = list(filter(lambda instruction: instruction['outpt_sk'][0] == stack_elem, user_instr))

                # It might be in the initial stack, so the list can be empty
                if previous_instr:
                    dependency_theta_graph[theta_id_act].add(previous_instr[0])

    return dependency_theta_graph


# Generate a dict that contains the real value as a key, and
# its associated index as a value.
def generate_phi_dict(user_instr):
    idx = 0
    phi = {}
    for instr in user_instr:
        for elem in instr['inpt_sk']:
            if type(elem) == int and elem not in phi:
                phi[elem] = idx
                idx += 1
    return phi


# Generate a dict that contains the theta associated to a
# instruction as values, and its corresponding opcode representation as values.
# Note that push has several possible opcodes depending on the size of the pushed value,
# and nop has no opcode associated. We will associated push to 60, the corresponding opcode
# for PUSH1.
def generate_disasm_map(user_instr, theta_instr):

    pattern_swap = re.compile("SWAP(.*)")
    pattern_dup = re.compile("DUP(.*)")

    instr_opcodes = {0: "60", 1: "50"}
    for id, theta in theta_instr.items():
        # This cases are already considered
        if id == "PUSH" or id == "POP" or id == "NOP":
            continue

        uninterpreted_function = True
        for match in re.finditer(pattern_swap, id):
            opcode = hex(int(match.group(1)) + int(str("90"), 16) - 1)[2:]
            uninterpreted_function = False
        for match in re.finditer(pattern_dup, id):
            opcode = hex(int(match.group(1)) + int(str("80"), 16) - 1)[2:]
            uninterpreted_function = False
        if uninterpreted_function:
            instr = list(filter(lambda instr: instr['id'] == id, user_instr))[0]
            opcode = instr['opcode']
        instr_opcodes[theta] = opcode

    return instr_opcodes

# Generate a dict that contains the theta associated to a instruction
# as keys and its corresponding EVM opcode as values. Note that it is similar
# to theta_comm and theta_non_comm, but instead of using id, we directly use
# disasm field (i.e. intead of having 14 : ADD_0, we would have 14 : ADD)
def generate_instr_map(user_instr, theta_stack, theta_comm, theta_non_comm):

    # We will consider in general the theta associated to instructions
    # in user instr structure
    theta_uninterpreted = dict(theta_comm, **theta_non_comm)

    # We reverse the theta stack, to have the theta value as key,
    # and its corresponding instruction as values
    theta_dict_reversed = {v: k for k, v in theta_stack.items()}
    for instr in user_instr:
        theta_value = theta_uninterpreted[instr['id']]
        disasm = instr['disasm']
        theta_dict_reversed[theta_value] = disasm

    return theta_dict_reversed