import random
from functools import reduce
from sympy import *
from plugins.problem_generator.utils import *

class AdditionProblem:
    skill_name = "addition"
    short_description = "Perform Addition."
    problem_enabled = True

    def __call__(self, digits=2, values=2):
        digits = convert_kwarg(digits, int)
        values = convert_kwarg(values, int)

        sym_vars = [''.join(['_', str(i)]) for i in range(0, values)]
        sym_list = list(symbols(' '.join(sym_vars)))
        expression = sum(sym_list)

        sym_values = []
        for v in sym_list:
            new_val = random_tens_int(digits)
            sym_values.append(str(new_val))
            expression = expression.subs(v, new_val)

        return ' + '.join(sym_values), str(expression)



class AdditionWordProblem:
    skill_name = "addition_word_problem"
    short_description = "Addition Word Problem."
    problem_enabled = False

    def __call__(self):
        pass



class SubtractionProblem:
    skill_name = "subtraction_problem"
    short_description = "Subtraction Problem."
    problem_enabled = True

    def __call__(self, digits=2, values=2):
        digits = convert_kwarg(digits, int)
        values = convert_kwarg(values, int)

        sym_vars = [''.join(['_', str(i)]) for i in range(0, values)]
        sym_list = list(symbols(' '.join(sym_vars)))
        expression = reduce(lambda x, y: x - y, sym_list)

        sym_values = []
        for v in sym_list:
            new_val = random_tens_int(digits)
            sym_values.append(str(new_val))
            expression = expression.subs(v, new_val)

        return ' - '.join(sym_values), str(expression)



class SubtractionWordProblem:
    skill_name = "subtraction_word_problem"
    short_description = "Subtraction Word Problem."
    problem_enabled = False

    def __call__(self):
        pass



class DivisionProblem:
    skill_name = "division_problem"
    short_description = "Division Problem."
    problem_enabled = True

    def __call__(self, dividend_digits=3, divisor_digits=2, rounding=2):
        dividend_digits = convert_kwarg(dividend_digits, int)
        divisor_digits = convert_kwarg(divisor_digits, int)
        rounding = convert_kwarg(rounding, int)

        dividend = random_tens_int(dividend_digits)
        divisor = random_tens_int(divisor_digits)

        problem_text = ' / '.join([str(dividend), str(divisor)])

        solutions = []
        #Solution #1
        float_solution = dividend / divisor
        if float_solution % 10 == 0:
            solutions.append(str(int(float_solution)))
        else:
            solutions.append(str(round(float_solution, rounding)))

        #Solution #2
        r = symbols('r')
        remainder = solve(Eq((dividend - r) / divisor, int(float_solution)))[0]
        solutions.append('r'.join([str(int(float_solution)), str(remainder)]))

        return problem_text, solutions



class DivisionWordProblem:
    skill_name = "division_word_problem"
    short_description = "Division Word Problem."
    problem_enabled = False

    def __call__(self):
        pass



class MultiplicationProblem:
    skill_name = "multiplication_problem"
    short_description = "Multiplication Problem."
    problem_enabled = True

    def __call__(self, digits=2, values=2):
        digits = convert_kwarg(digits, int)
        values = convert_kwarg(values, int)

        sym_vars = [''.join(['_', str(i)]) for i in range(0, values)]
        sym_list = list(symbols(' '.join(sym_vars)))
        expression = reduce(lambda x, y: x * y, sym_list)

        sym_values = []
        for v in sym_list:
            new_val = random_tens_int(digits)
            sym_values.append(str(new_val))
            expression = expression.subs(v, new_val)

        return ' * '.join(sym_values), str(expression)



class MultiplicationWordProblem:
    skill_name = "multiplication_word_problem"
    short_description = "Multiplication Word Problem."
    problem_enabled = False

    def __call__(self):
        pass



class OrderOfOperationsProblem:
    skill_name = "order_of_operations"
    short_description = "Order of Operations"
    problem_enabled = True

    def __call__(self, depth=2, rounding=2):
        depth = convert_kwarg(depth, int)

        expression = random_expression()
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



        return format_expression(expression), str(round(expression.evalf(), rounding))



class OrderOfOperationsWithAbsValuesProblem:
    skill_name = "order_of_operations_abs_values"
    short_description = "Order of Operations with Absolute Values."
    problem_enabled = False

    def __call__(self):
        pass
