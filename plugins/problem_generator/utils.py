import os
import json
import random
from sympy import *
from markdown import markdown

def load_problem_data():
    app_data = None
    with open('data.json') as f:
        app_data = json.loads(f.read())

    return app_data


def load_readme():
    readme = None
    with open('README.md') as f:
        readme = markdown(f.read(), extensions=['tables'])

    return readme

def convert_kwarg(kwarg, typ):
    if type(kwarg) == list:
        kwarg = kwarg[0]

    if type(kwarg) == str:
        kwarg = typ(kwarg)

    return kwarg


def format_expression(expression):
    expression = str(expression)
    expression = expression.replace('**', '^')
    expression = expression.replace('(-1)*', '-')
    expression = expression.replace('==', '=')
    return expression


def random_tens_int(digits):
    return random.randint(10**(digits-1), (10**digits)-1)


def random_expression(exp_a=None, exp_b=None):
    if not exp_a:
        exp_a = S(random_tens_int(random.choice([1,2,3])))

    if not exp_b:
        exp_b = S(random_tens_int(random.choice([1, 2, 3])))

    operations = None
    with evaluate(False):
        operations = [
            Add(exp_a, exp_b),
            Add(exp_a, Mul(exp_b, -1)),
            Mul(exp_a, exp_b),
            Mul(exp_a, 1 / exp_b),
            Add(Add(exp_a, exp_b), Pow(random_tens_int(1), random.randint(2, 3)))
        ]

    return random.choice(operations)

