from functools import reduce
from utils import convert_kwarg
import random
from sympy import *


# def dividing_polynomials_iii():
#     pass


def polynomials_in_standard_form():
    terms = [str(random.randint(0, 10)) for x in range(0, 4)]
    terms[0] = ''.join([terms[0], 'x^3'])
    terms[1] = ''.join([terms[1], 'x^2'])
    terms[2] = ''.join([terms[2], 'x'])
    solution = ' + '.join(terms)

    random.shuffle(terms)
    question = "Write the polynomial in standard form: " + ' + '.join(terms)

    return question, solution


# def graphing_a_quadratic_inequality():
#     pass


# def dividing_polynomials_ii():
#     pass


# def adding_and_subtracting_polynomials_with_common_denominators():
#     pass


# def distributing_with_polynomials_word_problem():
#     pass


# def distributing_with_polynomials():
#     pass


# def dividing_polynomials_by_one_term():
#     pass


# def multiplying_functions():
#     pass


# def graphing_a_quadratic_by_finding_the_vertex_and_the_x_intercepts():
#     pass


# def adding_and_subtracting_functions():
#     pass


# def multiplying_binomials():
#     pass


# def graphing_a_quadratic_by_using_an_x_y_table():
#     pass


# def simplifying_polynomials():
#     pass


# def dividing_functions():
#     pass


# def multiplying_functions_without_a_leading_coefficient():
#     pass


# def multiplying_polynomials():
#     pass


# def adding_and_subtracting_polynomials():
#     pass

