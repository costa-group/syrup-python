# Module that contains parameter declarations and
# other auxiliary methods to generate the encoding

from smtlib_utils import *
from collections import OrderedDict


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