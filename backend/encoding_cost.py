from encoding_utils import *
from encoding_files import write_encoding

# Soft constraints

# Label name for soft constraints
label_name = 'gas'


# Generates the soft constraints contained in the paper.
def paper_soft_constraints(b0, bs, user_instr, theta_stack, theta_comm, theta_non_comm, is_barcelogic=False):
    write_encoding("; Soft constraints from paper")
    instr_costs = generate_costs_ordered_dict(bs, user_instr, theta_stack, theta_comm, theta_non_comm)
    disjoin_sets = generate_disjoint_sets_from_cost(instr_costs)
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
            write_encoding(add_assert_soft(add_or(*list(map(lambda var: add_eq(t(j), var), or_variables))), wi,
                                           label_name, is_barcelogic))
        for instr in disjoin_sets[gas_cost]:
            or_variables.append(instr)

        # We update previous_cost
        previous_cost = gas_cost


# Method for generating an alternative model for soft constraints. This method is similar to the previous one,
# but instead it is based on inequalities and shorter constraints. See new paper for more details
def alternative_soft_constraints(b0, bs, user_instr, theta_stack, theta_comm, theta_non_comm, is_barcelogic=False):
    write_encoding("; Alternative soft constraints model")
    instr_costs = generate_costs_ordered_dict(bs, user_instr, theta_stack, theta_comm, theta_non_comm)

    # For every instruction and every position in the sequence, we add a soft constraint
    for theta_instr, gas_cost in instr_costs.items():
        if gas_cost == 0:
            continue

        for j in range(b0):
            write_encoding(add_assert_soft(add_not(add_eq(t(j), theta_instr)), gas_cost, label_name, is_barcelogic))