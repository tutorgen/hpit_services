import random
from functools import reduce
from sympy import *
from hpit.plugins.problem_generator.utils import *


class DividingPolynomialsIIIProblem:
    skill_name = "dividing_polynomials_iii"
    short_description = "Dividing Polynomials III"
    problem_enabled = False

    def __call__(self):
        pass



class PolynomialsInStandardFormProblem:
    skill_name = "polynomials_in_standard_form"
    short_description = "Polynomials in Standard Form"
    problem_enabled = True

    def __call__(self):
        terms = [str(random.randint(0, 10)) for x in range(0, 4)]
        terms[0] = ''.join([terms[0], 'x^3'])
        terms[1] = ''.join([terms[1], 'x^2'])
        terms[2] = ''.join([terms[2], 'x'])
        solution = ' + '.join(terms)

        random.shuffle(terms)
        question = "Write the polynomial in standard form: " + ' + '.join(terms)

        return question, solution



class GraphingAQuadraticInequalityProblem:
    skill_name = "graphing_a_quadratic_inequality"
    short_description = "Graphing A Quadratic Inequality"
    problem_enabled = False

    def __call__(self):
        pass



class DividingPolynomialsIIProblem:
    skill_name = "dividing_polynomials_ii"
    short_description = "Dividing Polynomials II"
    problem_enabled = False

    def __call__(self):
        pass



class AddingAndSubtractingPolynomialsWithCommonDenominatorsProblem:
    skill_name = "adding_and_subtracting_polynomials_with_common_denominators"
    short_description = "Adding and Subtracting Polynomials with Common Denominators"
    problem_enabled = False

    def __call__(self):
        pass



class DistributingWithpolynomialsWordProblem:
    skill_name = "distributing_with_polynomials_word_problem"
    short_description = "Distribution with Polynomials Word Problem"
    problem_enabled = False

    def __call__(self):
        pass



class DistributingWithPolynomialsProblem:
    skill_name = "distributing_with_polynomials"
    short_description = "Distributing with Polynomials"
    problem_enabled = False

    def __call__(self):
        pass



class DividingPolynomialsByOneTermProblem:
    skill_name = "dividing_polynomials_by_one_term"
    short_description = "Dividing Polynomials By One Term"
    problem_enabled = False

    def __call__(self):
        pass



class MultiplyingFunctionsProblem:
    skill_name = "multiplying_functions"
    short_description = "Multiplying Functions"
    problem_enabled = False

    def __call__(self):
        pass



class GraphingAQuadraticByFindingTheVertexAndTheXInterceptsProblem:
    skill_name = "graphing_a_quadratic_by_finding_the_vertex_and_the_x_intercepts"
    short_description = "Graphing A Quadratic By Finding The Vertex And THe X Intercepts Problem"
    problem_enabled = False

    def __call__(self):
        pass



class AddingAndSubtractingFunctionsProblem:
    skill_name = "adding_and_subtracting_functions"
    short_description = "Adding and Subtracting Functions"
    problem_enabled = False

    def __call__(self):
        pass



class MultiplyingBinomialsProblem:
    skill_name = "multiplying_binomials"
    short_description = "Multiplying Binomials"
    problem_enabled = False

    def __call__(self):
        pass



class GraphingAQuadraticByUsingAndXYTableProblem:
    skill_name = "graphing_a_quadratic_by_using_an_x_y_table"
    short_description = "Graphing a Quadratic by using an X, Y Table"
    problem_enabled = False

    def __call__(self):
        pass



class SimplifyingPolynomialsProblem:
    skill_name = "simplifying_polynomials"
    short_description = "Simplifying Polynomials"
    problem_enabled = False

    def __call__(self):
        pass



class DividingFunctionsProblem:
    skill_name = "dividing_functions"
    short_description = "Dividing Functions"
    problem_enabled = False

    def __call__(self):
        pass



class MultiplyingFunctionsWithoutALeadingCoefficientProblem:
    skill_name = "multiplying_functions_without_a_leading_coefficient"
    short_description = "Multiplying Functions without a leading coefficient"
    problem_enabled = False

    def __call__(self):
        pass



class MultiplyingPolynomialsProblem:
    skill_name = "multiplying_polynomials"
    short_description = "Multiplying Polynomials"
    problem_enabled = False

    def __call__(self):
        pass



class AddingAndSubtractingPolynomialsProblem:
    skill_name = "adding_and_subtracting_polynomials"
    short_description = "Adding And Subtracing Polynomials"
    problem_enabled = False

    def __call__(self):
        pass
