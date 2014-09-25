from functools import reduce
from utils import convert_kwarg, format_expression, random_expression, random_tens_int
import random
from sympy import *

# def solving_equations_with_the_distributive_property_and_by_combining_like_terms():
#     pass


# def solving_two_step_equations_simple_values():
#     pass


# def work_word_problems():
#     pass


# def solving_equations_with_the_distributive_property_first_step():
#     pass


def solving_two_step_equations(depth=2, rounding=2):
    depth = convert_kwarg(depth, int)

    expression = symbols('x')
    for t in range(0, depth-1):
        exp_type = random.choice(['left', 'right', 'center_left', 'center_right'])

        if exp_type == 'left':
            expression = random_expression(expression)
        elif exp_type == 'right':
            expression = random_expression(None, expression)
        elif exp_type == 'center_left':
            expression = random_expression(expression, random_expression())
        elif exp_type == 'center_right':
            expression = random_expression(random_expression(), expression)

    expression = Eq(expression, random_tens_int(2))
    solution = solve(expression)

    if not solution:
        return solving_two_step_equations(depth, rounding)

    solution = solution[0]
    solution_1 = format_expression(solution)
    solution_2 = str(round(solution.evalf(), rounding))
    return "Solve for x: " + format_expression(expression), [solution_1, solution_2]


# def work_word_problems_find_an_individual_time():
#     pass


# def solving_two_step_equations_variable_on_the_right():
#     pass


# def solving_equations_with_absolute_values_i():
#     pass


# def solving_equations_with_inequalities_and_absolute_values():
#     pass


# def solving_equations_with_the_distributive_property():
#     pass


# def solving_equations_by_combining_like_terms_i():
#     pass


# def direct_and_indirect_variation_squared_word_problems():
#     pass


# def solving_rational_expressions_i():
#     pass


# def rate_word_problems_ii():
#     pass


# def solving_with_variables_on_both_sides():
#     pass


# def solving_an_equation_word_problem():
#     pass


# def solving_equations_with_absolute_values_ii():
#     pass


# def solving_equations_by_combining_like_terms_ii():
#     pass


# def solving_equations_with_inequalities():
#     pass


# def solving_for_a_variable_in_terms_of_other_variables_more_advanced():
#     pass


# def solving_two_step_equations_simple_values_no_negatives():
#     pass


# def rate_word_problems_iii():
#     pass


# def direct_and_indirect_variation_word_problems():
#     pass


# def solving_multi_step_equation_word_problem():
#     pass


# def solving_for_a_variable_in_terms_of_other_variables():
#     pass


# def solving_rational_expressions_ii():
#     pass


# def rate_word_problems_i():
#     pass


# def solving_with_variables_on_both_sides_1_digit():
#     pass
