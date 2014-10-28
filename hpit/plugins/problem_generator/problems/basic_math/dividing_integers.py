import random
from functools import reduce
from sympy import *
from hpit.plugins.problem_generator.utils import *




class MultiplyingIntegersProblem:
    skill_name = "multiplying_integers"
    short_description = "Multiplying integers."
    problem_enabled = False

    def __call__(self):
        return False



class EvaluatingExpressionsBasicOneOperationProblem:
    skill_name = "evaluating_expressions_basic_one_operation"
    short_description = "Evaluating expressions (Basic one operation)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByAdditionProblem:
    skill_name = "solving_single_step_equations_by_addition"
    short_description = "Solving single-step equations by addition."
    problem_enabled = False

    def __call__(self):
        return False



class GivenAGraphCalculateTheSlopeProblem:
    skill_name = "given_a_graph_calculate_the_slope"
    short_description = "Given a graph, calculate the slope."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByAdditionOrSubtraction1DigitProblem:
    skill_name = "solving_single_step_equations_by_addition_or_subtraction_1_digit"
    short_description = "Solving single-step equations by addition or subtraction (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class AddingIntegersProblem:
    skill_name = "adding_integers"
    short_description = "Adding integers."
    problem_enabled = False

    def __call__(self):
        return False



class EvaluateABasicRootProblem:
    skill_name = "evaluate_a_basic_root"
    short_description = "Evaluate a basic root."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByAddition1DigitNoNegativesProblem:
    skill_name = "solving_single_step_equations_by_addition_1_digit_no_negatives"
    short_description = "Solving single-step equations by addition (1-digit no negatives)."
    problem_enabled = False

    def __call__(self):
        return False



class Adding34IntegersProblem:
    skill_name = "adding_3_4_integers"
    short_description = "Adding 3 - 4 integers."
    problem_enabled = False

    def __call__(self):
        return False



class EvaluatingExpressionsIiProblem:
    skill_name = "evaluating_expressions_ii"
    short_description = "Evaluating expressions II."
    problem_enabled = False

    def __call__(self):
        return False



class FunctionsProblem:
    skill_name = "functions"
    short_description = "Functions."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsBySubtractionProblem:
    skill_name = "solving_single_step_equations_by_subtraction"
    short_description = "Solving single-step equations by subtraction."
    problem_enabled = False

    def __call__(self):
        return False



class FunctionsTableProblem:
    skill_name = "functions_table"
    short_description = "Functions - Table."
    problem_enabled = False

    def __call__(self):
        return False



class EvaluatingExpressionsBasicTwoOperationsProblem:
    skill_name = "evaluating_expressions_basic_two_operations"
    short_description = "Evaluating expressions (Basic two operations)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingTwoStepEquationsProblem:
    skill_name = "solving_two_step_equations"
    short_description = "Solving two-step equations."
    problem_enabled = False

    def __call__(self):
        return False



class ApplyingAreaFormulasProblem:
    skill_name = "applying_area_formulas"
    short_description = "Applying area formulas."
    problem_enabled = False

    def __call__(self):
        return False



class AddingIntegers1DigitProblem:
    skill_name = "adding_integers_1_digit"
    short_description = "Adding integers (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class FindTheSlopeGiven2PointsProblem:
    skill_name = "find_the_slope_given_2_points"
    short_description = "Find the slope given 2 points."
    problem_enabled = False

    def __call__(self):
        return False



class GraphALineGivenAnEquationInSlopeInterceptFormProblem:
    skill_name = "graph_a_line_given_an_equation_in_slope_intercept_form"
    short_description = "Graph a line given an equation in slope-intercept form."
    problem_enabled = False

    def __call__(self):
        return False



class IntegerWordProblemProblem:
    skill_name = "integer_word_problem"
    short_description = "Integer word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SubtractingIntegers1DigitProblem:
    skill_name = "subtracting_integers_1_digit"
    short_description = "Subtracting integers (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingTwoStepEquationsSimpleValuesProblem:
    skill_name = "solving_two_step_equations_simple_values"
    short_description = "Solving two-step equations (simple values)."
    problem_enabled = False

    def __call__(self):
        return False



class MultiplyingIntegers1DigitProblem:
    skill_name = "multiplying_integers_1_digit"
    short_description = "Multiplying integers (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class EvaluatingExpressionsIProblem:
    skill_name = "evaluating_expressions_i"
    short_description = "Evaluating expressions I."
    problem_enabled = False

    def __call__(self):
        return False



class BasicExponentsPowersProblem:
    skill_name = "basic_exponents_powers"
    short_description = "Basic exponents (powers)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByMultiplication1DigitNoNegativesProblem:
    skill_name = "solving_single_step_equations_by_multiplication_1_digit_no_negatives"
    short_description = "Solving single-step equations by multiplication (1-digit no negatives)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsBySubtraction1DigitNoNegativesProblem:
    skill_name = "solving_single_step_equations_by_subtraction_1_digit_no_negatives"
    short_description = "Solving single-step equations by subtraction (1-digit no negatives)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByMultiplicationProblem:
    skill_name = "solving_single_step_equations_by_multiplication"
    short_description = "Solving single-step equations by multiplication."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByAdditionOrSubtractionProblem:
    skill_name = "solving_single_step_equations_by_addition_or_subtraction"
    short_description = "Solving single-step equations by addition or subtraction."
    problem_enabled = False

    def __call__(self):
        return False



class Multiplying34Integers1DigitProblem:
    skill_name = "multiplying_3_4_integers_1_digit"
    short_description = "Multiplying 3 - 4 integers (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class GivenAPointAndAnEquationInSlopeInterceptFormDetermineIfThePointExistsOnTheLineProblem:
    skill_name = "given_a_point_and_an_equation_in_slope_intercept_form_determine_if_the_point_exists_on_the_line"
    short_description = "Given a point and an equation in slope-intercept form, determine if the point exists on the line."
    problem_enabled = False

    def __call__(self):
        return False



class AddingIntegersWordProblemProblem:
    skill_name = "adding_integers_word_problem"
    short_description = "Adding integers word problem."
    problem_enabled = False

    def __call__(self):
        return False



class Adding34Integers1DigitProblem:
    skill_name = "adding_3_4_integers_1_digit"
    short_description = "Adding 3 - 4 integers (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByDivisionProblem:
    skill_name = "solving_single_step_equations_by_division"
    short_description = "Solving single-step equations by division."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsBySubtraction1DigitProblem:
    skill_name = "solving_single_step_equations_by_subtraction_1_digit"
    short_description = "Solving single-step equations by subtraction (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByAddition1DigitProblem:
    skill_name = "solving_single_step_equations_by_addition_1_digit"
    short_description = "Solving single-step equations by addition (1-digit)."
    problem_enabled = False

    def __call__(self):
        return False



class SolvingSingleStepEquationsByDivisionSimpleValuesNoNegativesProblem:
    skill_name = "solving_single_step_equations_by_division_simple_values_no_negatives"
    short_description = "Solving single-step equations by division (simple values no negatives)."
    problem_enabled = False

    def __call__(self):
        return False



class GraphByUsingAnXYTableYIsIsolatedProblem:
    skill_name = "graph_by_using_an_x_y_table_y_is_isolated"
    short_description = "Graph by using an x-y table (y is isolated)."
    problem_enabled = False

    def __call__(self):
        return False



class DividingIntegers12DigitsProblem:
    skill_name = "dividing_integers_1_2_digits"
    short_description = "Dividing integers (1-2 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class SubtractingIntegersProblem:
    skill_name = "subtracting_integers"
    short_description = "Subtracting integers."
    problem_enabled = False

    def __call__(self):
        return False



class PlotAPointOnACoordinatePlaneProblem:
    skill_name = "plot_a_point_on_a_coordinate_plane"
    short_description = "Plot a point on a coordinate plane."
    problem_enabled = False

    def __call__(self):
        return False



class DividingIntegersProblem:
    skill_name = "dividing_integers"
    short_description = "Dividing integers."
    problem_enabled = False

    def __call__(self):
        return False


