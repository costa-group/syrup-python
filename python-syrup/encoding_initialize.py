from encoding_files import write_encoding
from encoding_utils import *

# Methods for initializing the variables

def _initialize_s_vars(variables):
    for var in variables:
        write_encoding(declare_intvar(var))


def _initialize_u_vars(bs, b0):
    for i in range(bs):
        for j in range(b0+1):
            write_encoding(declare_boolvar(u(i,j)))


def _initialize_x_vars(bs, b0):
    for i in range(bs):
        for j in range(b0+1):
            write_encoding(declare_intvar(x(i,j)))


def _initialize_t_vars(b0):
    for i in range(b0):
        write_encoding(declare_intvar(t(i)))


def _initialize_a_vars(b0):
    for i in range(b0):
        write_encoding(declare_intvar(a(i)))


def initialize_variables(variables, bs, b0):
    _initialize_s_vars(variables)
    _initialize_u_vars(bs, b0)
    _initialize_x_vars(bs, b0)
    _initialize_t_vars(b0)
    _initialize_a_vars(b0)


# Method for generating variable assignment (SV)

def variables_assignment_constraint(variables):
    write_encoding("; Variables assignment")
    for i, var in enumerate(variables):
        statement = add_eq(var, int_limit + i)
        write_encoding(add_assert(statement))


# Methods for defining how the stack at the beginning is (B)

def initial_stack_encoding(initial_stack, bs):
    write_encoding("; Initial stack constraints")

    for alpha, variable in enumerate(initial_stack):
        write_encoding(add_assert(add_and(u(alpha, 0), add_eq(x(alpha, 0), variable))))

    for beta in range(len(initial_stack), bs):
        write_encoding(add_assert(add_not(u(beta, 0))))


# Methods for defining how the stack at the end is (E)


def final_stack_encoding(final_stack, bs, b0):
    write_encoding("; Final stack constraints")

    for alpha, variable in enumerate(final_stack):
        write_encoding(add_assert(add_and(u(alpha, b0), add_eq(x(alpha, b0), variable))))

    for beta in range(len(final_stack), bs):
        write_encoding(add_assert(add_not(u(beta, b0))))