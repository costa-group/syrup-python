import unittest
from backend.encoding_utils import generate_number_of_previous_instr_dict

class Test_Encoding_Utils(unittest.TestCase):

    def test_prev_instructions_repeated_values(self):
        dependency_graph = {'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)]}
        expected_output = {'INSTR_0': 2, 'INSTR_1': 0, 'INSTR_2': 5, 'INSTR_3': 8, 'INSTR_4': 11}
        self.assertDictEqual(expected_output, generate_number_of_previous_instr_dict(dependency_graph))

    def test_prev_instructions_several_maximal_elements(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)],
                            'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_2', -1)],
                            'INSTR_6': [('INSTR_4', -1), ('INSTR_5', -1), ('INSTR_2', -1)]}
        expected_output = {'INSTR_0': 2, 'INSTR_1': 0, 'INSTR_2': 5, 'INSTR_3': 8,
                           'INSTR_4': 11, 'INSTR_5': 11, 'INSTR_6': 17}
        self.assertDictEqual(expected_output, generate_number_of_previous_instr_dict(dependency_graph))


if __name__ == '__main__':
    unittest.main()
