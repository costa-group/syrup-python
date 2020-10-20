# Methods containing the generation of constraints
# for applying superoptimization. It is assumed the
# SFS has already been generated

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

# Methods for initializing the variables

def _initialize_s_vars(variables):
    for var in variables:
        print(declare_intvar(var))


def _initialize_u_vars(bs, b0):
    for i in range(bs):
        for j in range(b0+1):
            print(declare_boolvar(u(i,j)))


def _initialize_x_vars(bs, b0):
    for i in range(bs):
        for j in range(b0+1):
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

def _move(j, alpha, beta, delta):
    and_variables = []

    # Move can be empty
    if alpha > beta:
        return "true"
    for i in range(alpha, beta+1):
        first_and = add_eq(u(i+delta, j+1), u(i,j))
        second_and = add_eq(x(i+delta, j+1), x(i,j))
        and_variables.append(add_and(first_and, second_and))
    return add_and(*and_variables)


def _generate_stack_theta(bs):
    theta = {}
    theta["PUSH"] = 0
    theta["POP"] = 1
    theta["NOP"] = 2
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

# Separes user instructions in two groups, according to whether they
# are commutative or not.
def _separe_usr_instr(user_instr):
    comm_functions = []
    non_comm_functions = []
    for instr in user_instr:
        if instr['commutative']:
            comm_functions.append(instr)
        else:
            non_comm_functions.append(instr)
    return comm_functions, non_comm_functions


# Method for generating variable assignment (SV)

def variables_assignment_constraint(variables):
    print("; Variables assignment")
    for i, var in enumerate(variables):
        statement = add_eq(var, int_limit + i)
        print(add_assert(statement))

# Methods for generating the constraints for stack (Cs)

def _push_encoding(j, bs, theta_push):
    left_term = add_eq(t(j), theta_push)
    right_term = add_and(add_leq(0, a(j)), add_lt(a(j), int_limit), add_not(u(bs-1,j)), u(0, j+1),
                          add_eq(x(0, j+1), a(j)), _move(j, 0, bs-2, 1))
    print(add_assert(add_implies(left_term, right_term)))


def _dupk_encoding(k, j, bs, theta_dupk):
    left_term = add_eq(t(j), theta_dupk)
    right_term = add_and(add_not(u(bs-1, j)), u(k-1, j), u(0, j+1),
                          add_eq(x(0, j+1), x(k-1, j)), _move(j, 0, bs-2, 1))
    print(add_assert(add_implies(left_term, right_term)))


def _swapk_encoding(k,j, bs, theta_swapk):
    left_term = add_eq(t(j), theta_swapk)
    right_term = add_and(u(k,j), u(0, j+1), add_eq(x(0, j+1), x(k,j)) ,
                          u(k, j+1), add_eq(x(k, j+1), x(0,j)),
                          _move(j, 1, k-1, 0), _move(j, k+1, bs-1, 0))
    print(add_assert(add_implies(left_term, right_term)))


def _pop_encoding(j, bs, theta_pop):
    left_term = add_eq(t(j), theta_pop)
    right_term = add_and(u(0,j), add_not(u(bs-1, j+1)), _move(j,1,bs-1,-1))
    print(add_assert(add_implies(left_term, right_term)))


def _nop_encoding(j, bs, theta_nop):
    left_term = add_eq(t(j), theta_nop)
    right_term = _move(j,0,bs-1,0)
    print(add_assert(add_implies(left_term, right_term)))


def _fromnop_encoding(b0, theta_nop):
    for j in range(b0-1):
        left_term = add_eq(t(j), theta_nop)
        right_term = add_eq(t(j+1), theta_nop)
        print(add_assert(add_implies(left_term, right_term)))


def _stack_constraints(b0, bs, theta):
    print("; Stack contraints")
    _fromnop_encoding(b0, theta["NOP"])
    for j in range(b0):
        _push_encoding(j, bs, theta["PUSH"])
        _pop_encoding(j, bs, theta["POP"])
        _nop_encoding(j, bs, theta["NOP"])

        for k in range(1, min(bs, max_k_dup + 1)):
            _dupk_encoding(k, j, bs, theta["DUP" + str(k)])

        for k in range(1, min(bs, max_k_swap + 1)):
            _swapk_encoding(k, j, bs, theta["SWAP" + str(k)])

# Methods for generating constraints for non-commutative uninterpreted functions (Cu)


def _non_comm_function_encoding(j, bs, o, r, theta_f):
    n = len(o)
    left_term = add_eq(t(j), theta_f)
    right_term_first_and = ["true"]
    # Second and can be empty, so we initialize terms to true value
    right_term_second_and = ["true"]
    for i in range(0, n):
        right_term_first_and.append(add_and(u(i,j), add_eq(x(i,j), o[i])))
    for i in range(bs-n+1, bs):
        right_term_second_and.append(add_not(u(i, j+1)))
    right_term = add_and(add_and(*right_term_first_and), u(0, j+1) , add_eq(x(0,j+1), r),
                          _move(j, n, min(bs-2+n, bs-1), 1-n) , add_and(*right_term_second_and))
    print(add_assert(add_implies(left_term, right_term)))


def non_comm_function_constraints(b0, bs, non_comm_user_instr, theta_non_comm):
    print("; Non-commutative constraints")
    for instr in non_comm_user_instr:
        o = instr['inpt_sk']
        theta_f = theta_non_comm[instr['id']]

        # We assume every function has only one output
        r = instr['outpt_sk'][0]

        for j in range(b0):
            _non_comm_function_encoding(j, bs, o, r, theta_f)

# Methods for generating constraints for commutative uninterpreted functions (Cc)

def _comm_function_encoding(j, bs, o0, o1, r, theta_f):
    left_term = add_eq(t(j), theta_f)
    right_term = add_and(u(0,j), u(1,j), add_or(add_and(add_eq(x(0,j), o0), add_eq(x(1,j), o1)),
                                                  add_and(add_eq(x(0,j), o1), add_eq(x(1,j), o0))),
                          u(0,j+1), add_eq(x(0,j+1), r), _move(j, 2, bs-1, -1), add_not(u(bs-1, j)))
    print(add_assert(add_implies(left_term, right_term)))


def comm_function_constraints(b0, bs, comm_user_instr, theta_comm):
    print("; Commutative constraints")
    for instr in comm_user_instr:
        o0 = instr['inpt_sk'][0]
        o1 = instr['inpt_sk'][1]
        theta_f = theta_comm[instr['id']]

        # We assume every function has only one output
        r = instr['outpt_sk'][0]

        for j in range(b0):
            _comm_function_encoding(j, bs, o0, o1, r, theta_f)

# Methods for generating constraints for finding the target program

def instructions_constraints(b0, bs, comm_instr, non_comm_instr, theta_stack, theta_comm, theta_non_comm):
    mi = len(theta_stack) + len(theta_comm) + len(theta_non_comm)
    print("; Instructions constraints")

    for j in range(b0):
        print(add_assert(add_and(add_leq(0, t(j)), add_lt(t(j), mi))))

    _stack_constraints(b0, bs, theta_stack)
    comm_function_constraints(b0, bs, comm_instr, theta_comm)
    non_comm_function_constraints(b0, bs, non_comm_instr, theta_non_comm)


# Methods for defining how the stack at the beginning is (B)

def initial_stack_encoding(initial_stack, bs):
    print("; Initial stack constraints")

    for alpha, variable in enumerate(initial_stack):
        print(add_assert(add_and(u(alpha, 0), add_eq(x(alpha, 0), variable))))

    for beta in range(len(initial_stack), bs):
        print(add_assert(add_not(u(beta, 0))))


# Methods for defining how the stack at the end is (E)


def final_stack_encoding(final_stack, bs, b0):
    print("; Final stack constraints")

    for alpha, variable in enumerate(final_stack):
        print(add_assert(add_and(u(alpha, b0), add_eq(x(alpha, b0), variable))))

    for beta in range(len(final_stack), bs):
        print(add_assert(add_not(u(beta, b0))))


# Aditional contraints

def _each_function_is_used(b0, initial_idx, end_idx):
    print("; All uninterpreted functions are eventually used")
    for i in range(initial_idx, end_idx):
        or_variables = []
        for j in range(b0):
            or_variables.append(add_eq(t(j), i))
        print(add_assert(add_or(*or_variables)))


# Soft constraints

# Generates an ordered dict that contains all instructions associated value of theta
# as keys, and their gas cost as values. Ordered by increasing costs
def _generate_costs_ordered_dict(bs, user_instr, theta_stack, theta_comm, theta_non_comm):
    instr_costs = {}
    instr_costs[theta_stack["PUSH"]] = 3
    instr_costs[theta_stack["POP"]] = 2
    instr_costs[theta_stack["NOP"]] = 0
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
def _generate_disjoint_sets_from_cost(ordered_costs):
    disjoint_set = {}
    for id in ordered_costs:
        gas_cost = ordered_costs[id]
        if gas_cost in disjoint_set:
            disjoint_set[gas_cost].append(id)
        else:
            disjoint_set[gas_cost] = [id]
    return OrderedDict(sorted(disjoint_set.items(), key=lambda t: t[0]))


# Generates the soft constraints contained in the paper.
def paper_soft_constraints(b0, bs, user_instr, theta_stack, theta_comm, thetha_non_comm):
    print("; Soft constraints from paper")
    instr_costs = _generate_costs_ordered_dict(bs, user_instr, theta_stack, theta_comm, thetha_non_comm)
    disjoin_sets = _generate_disjoint_sets_from_cost(instr_costs)
    previous_cost = 0
    or_variables = []
    for gas_cost in disjoin_sets:
        # We skip the first set of instructions, as they have
        # no soft constraint associated. Neverthelss, we add
        # opcodes with cost 0 to the set of variables till p
        if gas_cost == 0:
            for instr in disjoin_sets[gas_cost]:
                or_variables.append(instr)
            continue

        wi = gas_cost - previous_cost

        # Before adding current associated opcodes, we generate
        # the constraints for each tj.
        for j in range(b0):
            print(add_assert_soft(add_or(*list(map(lambda var: add_eq(t(j), var), or_variables))), wi, 'gas'))
        for instr in disjoin_sets[gas_cost]:
            or_variables.append(instr)

        # We update previous_cost
        previous_cost = gas_cost

# Method to generate complete representation

def generate_smtlib_encoding(b0, bs, usr_instr, variables, initial_stack, final_stack):
    set_logic('QF_LIA')
    initialize_variables(variables, bs, b0)
    variables_assignment_constraint(variables)
    theta_stack = _generate_stack_theta(bs)
    theta_comm, theta_non_comm = _generate_uninterpreted_theta(usr_instr, len(theta_stack))
    comm_instr, non_comm_instr = _separe_usr_instr(usr_instr)
    instructions_constraints(b0, bs, comm_instr, non_comm_instr, theta_stack, theta_comm, theta_non_comm)
    initial_stack_encoding(initial_stack, bs)
    final_stack_encoding(final_stack, bs, b0)
    _each_function_is_used(b0, len(theta_stack), len(theta_stack) + len(theta_comm) + len(theta_non_comm))
    paper_soft_constraints(b0, bs, usr_instr, theta_stack, theta_comm, theta_non_comm)
    check_sat()
    get_objectives()
    # get_model()
    for j in range(b0):
        get_value(t(j))
        get_value(a(j))
    print("; Stack: " + str(theta_stack))
    print("; Comm: " + str(theta_comm))
    print("; Non-Comm: " + str(theta_non_comm))
