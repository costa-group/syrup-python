import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/backend")
from encoding_utils import generate_number_of_previous_instr_dict, generate_first_position_instr_cannot_appear



class Test_Encoding_Utils(unittest.TestCase):

    def test_prev_instructions_repeated_values(self):
        dependency_graph = {'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)]}
        expected_output = {'INSTR_0': 2, 'INSTR_1': 0, 'INSTR_2': 5, 'INSTR_3': 8, 'INSTR_4': 11, 'PUSH': 0}
        output = generate_number_of_previous_instr_dict(dependency_graph)
        self.assertDictEqual(expected_output, output)

    def test_prev_instructions_several_maximal_elements(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)],
                            'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_2', -1)],
                            'INSTR_6': [('INSTR_4', -1), ('INSTR_5', -1), ('INSTR_2', -1)]}
        expected_output = {'INSTR_0': 2, 'INSTR_1': 0, 'INSTR_2': 5, 'INSTR_3': 8,
                           'INSTR_4': 11, 'INSTR_5': 11, 'INSTR_6': 17, 'PUSH': 0}
        output = generate_number_of_previous_instr_dict(dependency_graph)
        self.assertDictEqual(expected_output, output)


    def test_prev_instructions_several_dependencies(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)],
                            'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_2', -1)],
                            'INSTR_6': [('INSTR_4', -1), ('INSTR_5', -1), ('INSTR_2', -1)],
                            'INSTR_7': [('PUSH', 3), ('PUSH', 7), ('INSTR_2', -1)]}
        expected_output = {'INSTR_0': 2, 'INSTR_1': 0, 'INSTR_2': 5, 'INSTR_3': 8,
                           'INSTR_4': 11, 'INSTR_5': 11, 'INSTR_6': 17, 'INSTR_7': 8, 'PUSH': 0}
        output = generate_number_of_previous_instr_dict(dependency_graph)
        self.assertDictEqual(expected_output, output)


    def test_first_position_cannot_appear_repeated_values(self):
        dependency_graph = {'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)]}
        b0 = 15
        final_stack_instr = ['INSTR_2', 'INSTR_4', 'INSTR_0']
        expected_output = {'INSTR_0': 11, 'INSTR_1': 11, 'INSTR_2': 12, 'INSTR_3': 13, 'INSTR_4': 14, 'PUSH': 15}
        output = generate_first_position_instr_cannot_appear(b0, final_stack_instr, dependency_graph)
        self.assertDictEqual(expected_output, output)


    def test_first_position_cannot_appear_several_maximal_elements(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)],
                            'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_2', -1)],
                            'INSTR_6': [('INSTR_4', -1), ('INSTR_5', -1), ('INSTR_2', -1)]}
        b0 = 17
        final_stack_instr = ['INSTR_0', 'INSTR_2', 'INSTR_6', 'INSTR_5']
        expected_output = {'INSTR_0': 12, 'INSTR_1': 12, 'INSTR_2': 13, 'INSTR_3': 14,
                           'INSTR_4': 15, 'INSTR_5': 15, 'INSTR_6': 16, 'PUSH': 17}
        output = generate_first_position_instr_cannot_appear(b0, final_stack_instr, dependency_graph)
        self.assertDictEqual(expected_output, output)


    def test_first_position_cannot_appear_several_dependencies(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_1', -1)],
                            'INSTR_3': [('INSTR_2', -1), ('PUSH', 8), ('INSTR_2', -1)],
                            'INSTR_4': [('INSTR_3', -1), ('INSTR_1', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_2', -1)],
                            'INSTR_6': [('INSTR_4', -1), ('INSTR_5', -1), ('INSTR_2', -1)],
                            'INSTR_7': [('PUSH', 3), ('PUSH', 7), ('INSTR_2', -1)]}
        b0 = 20
        final_stack_instr = ['INSTR_7', 'INSTR_6']
        expected_output = {'INSTR_0': 15, 'INSTR_1': 15, 'INSTR_2': 16, 'INSTR_3': 17,
                           'INSTR_4': 18, 'INSTR_5': 18, 'INSTR_6': 19, 'INSTR_7': 20, 'PUSH': 20}
        output = generate_first_position_instr_cannot_appear(b0, final_stack_instr, dependency_graph)
        self.assertDictEqual(expected_output, output)


    def test_first_position_cannot_appear_elements_from_diff_trees(self):
        dependency_graph = {'INSTR_0': [('PUSH', 5), ('PUSH', 6)], 'INSTR_1': [],
                            'INSTR_2': [('INSTR_0', -1), ('PUSH', 7), ('INSTR_0', -1)],
                            'INSTR_3': [('INSTR_1', -1), ('PUSH', 8), ('INSTR_1', -1)],
                            'INSTR_4': [('INSTR_2', -1), ('INSTR_2', -1), ('INSTR_2', -1)],
                            'INSTR_5': [('INSTR_3', -1), ('INSTR_3', -1), ('INSTR_3', -1)],
                            'INSTR_6': [('INSTR_2', -1), ('INSTR_5', -1), ('INSTR_2', -1)],
                            'INSTR_7': [('INSTR_3', 3), ('INSTR_9', 7), ('INSTR_4', -1)],
                            'INSTR_8': [('PUSH', 3), ('INSTR_6', 7), ('INSTR_6', -1)],
                            'INSTR_9': [('PUSH', 3), ('INSTR_2', 7), ('INSTR_2', -1)]}
        b0 = 20
        final_stack_instr = ['INSTR_8', 'INSTR_7']
        expected_output = {'INSTR_0': 16, 'INSTR_1': 16, 'INSTR_2': 17, 'INSTR_3': 17,
                           'INSTR_4': 18, 'INSTR_5': 18, 'INSTR_6': 19, 'INSTR_7': 19,
                           'INSTR_8': 20, 'INSTR_9': 18, 'PUSH': 20}
        output = generate_first_position_instr_cannot_appear(b0, final_stack_instr, dependency_graph)
        self.assertDictEqual(expected_output, output)

if __name__ == '__main__':
    unittest.main()
