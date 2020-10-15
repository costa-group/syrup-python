# Methods containing the generation of constraints
# for applying superoptimization. It is assumed the
# SFS has already been generated

from smtlib_utils import *

# We set the maximum k dup and swap instructions
# can have.

max_k_dup = 16
max_k_swap = 16

# Maximum size integers have in the EVM

int_limit = 2**256

# Methods for generating string corresponding to
# variables we will be using for the encoding


def u(i,j):
    return var2str("u", [i,j])


def x(i,j):
    return var2str("x", [i,j])


def t(i):
    return var2str('t', [i])


def a(i):
    return var2str('a', [i])

# Methods for initializing the variables

def _initialize_s_vars(variables):
    for var in variables:
        print(declare_intvar(var))


def _initialize_u_vars(bs, b0):
    for i in range(bs-1):
        for j in range(b0):
            print(declare_intvar(u(i,j)))


def _initialize_x_vars(bs, b0):
    for i in range(bs-1):
        for j in range(b0):
            print(declare_intvar(x(i,j)))


def _initialize_t_vars(b0):
    for i in range(b0):
        print(declare_intvar(t(i)))


def _initialize_a_vars(b0):
    for i in range(b0):
        print(declare_intvar(a(i)))


def initialize_variables(variables, bs, b0):
    _initialize_s_vars(variables)
    _initialize_u_vars(bs, b0)
    _initialize_x_vars(bs, b0)
    _initialize_t_vars(b0)
    _initialize_a_vars(b0)



# Auxiliary methods for defining the constraints

def _move(j, alpha, beta, sigma):
    and_variables = []
    for i in range(alpha, beta+1):
        first_and = add_eq([u(i+sigma, j+1), u(i,j)])
        second_and = add_eq([x(i+sigma, j+1), x(i,j)])
        and_variables.append(add_and([first_and, second_and]))
    return add_and(and_variables)

def _generate_stack_theta(b0):
    tetha = {}
    tetha["PUSH"] = 0
    tetha["POP"] = 1
    tetha["NOP"] = 2
    initial_index = 3
    for i in range(1, min(b0, max_k_dup+1)):
        tetha["DUP" + str(i)] = initial_index
        initial_index += 1
    for i in range(1, min(b0, max_k_swap+1)):
        tetha["SWAP" + str(i)] = initial_index
        initial_index += 1
    return tetha


# Returns two different dictionaries: the first one, for
# commutative functions and the second one for
# non-commutative functions
def _generate_uninterpreted_theta(user_instr, initial_index):
    theta_comm = {}
    theta_non_comm = {}
    for instr in user_instr:
        if instr['commutative']:
            theta_comm[instr['id']] = initial_index
        else:
            theta_non_comm[instr['id']] = initial_index
        initial_index += 1
    return theta_comm, theta_non_comm

# Method for generating variable assignment (SV)

def _variables_assignment_constraint(variables):
    print("; Variables assignment")
    for i,var in enumerate(variables):
        statement = add_eq([var, int_limit + i])
        print(add_assert(statement))

# Methods for generating the constraints for stack (Cs)

def _push_encoding(j, bs, theta_push):
    left_term = add_eq([t(j), theta_push])
    right_term = add_and([add_leq([0, a(j)]), add_lt([a(j), int_limit]), add_not(u(bs-1,j)), u(0, j+1),
                          add_eq([x(0, j+1), a(j)]), _move(j, 0, bs-2, 1)])
    print(add_assert(add_implies([left_term, right_term])))


def _dupk_encoding(k, j, bs, theta_dupk):
    left_term = add_eq([t(j), theta_dupk])
    right_term = add_and([add_not(u(bs-1, j)), u(k-1, j), u(0, j+1),
                          add_eq([x(0, j+1), x(k-1, j)]), _move(j, 0, bs-2, 1)])
    print(add_assert(add_implies([left_term, right_term])))


def _swapk_encoding(k,j, bs, theta_swapk):
    left_term = add_eq([t(j), theta_swapk])
    right_term = add_and([u(k,j), u(0, j+1), add_eq([x(0, j+1), x(k,j)]) ,
                          u(k, j+1), add_eq([x(k, j+1), x(0,j)]),
                          _move(j, 1, k-1, 0), _move(j, k+1, bs-1, 0)])
    print(add_assert(add_implies([left_term, right_term])))


def _pop_encoding(j, bs, theta_pop):
    left_term = add_eq([t(j), theta_pop])
    right_term = add_and([u(0,j), add_not(u(bs-1, j+1)), _move(j,1,bs-1,-1)])
    print(add_assert(add_implies([left_term, right_term])))


def _nop_encoding(j, bs, theta_nop):
    left_term = add_eq([t(j), theta_nop])
    right_term = _move(j,0,bs-1,0)
    print(add_assert(add_implies([left_term, right_term])))


def _fromnop_encoding(b0, theta_nop):
    for j in range(b0-1):
        left_term = add_eq([t(j), theta_nop])
        right_term = add_eq([t(j+1), theta_nop])
        print(add_assert(add_implies([left_term, right_term])))


def _stack_constraints(b0, bs, theta):
    print("; Stack contraints")
    _fromnop_encoding(b0, theta["NOP"])
    for j in range(b0):
        _push_encoding(j, bs, theta["PUSH"])
        _pop_encoding(j, bs, theta["POP"])
        _nop_encoding(j, bs, theta["NOP"])

        for k in range(1, min(b0, max_k_dup + 1)):
            _dupk_encoding(k, j, bs, theta["DUP"])

        for k in range(1, min(b0, max_k_dup + 1)):
            _dupk_encoding(k, j, bs, theta["DUP"])



def generate_smtlib_encoding(b0, bs, usr_instr, variables):
    pass
