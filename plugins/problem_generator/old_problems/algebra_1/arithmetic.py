from functools import reduce
from utils import convert_kwarg, format_expression, random_expression
import random
from sympy import *

def addition(digits=2, values=2):
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

#def addition_word_problems():
#    pass

def subtraction(digits=2, values=2):
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

# def subtraction_word_problem():
#     pass

def division(dividend_digits=3, divisor_digits=1, rounding=2):
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

# def division_word_problem():
#     pass

def multiplication(digits=2, values=2):
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

# def multiplication_word_problem():
#     pass

def order_of_operations(depth=2, rounding=2):
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

# def order_of_operations_ii():
#     pass

# def order_of_operations_with_absolute_values():
#     pass
