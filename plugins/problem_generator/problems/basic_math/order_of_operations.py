
import random
from functools import reduce
from sympy import *
from plugins.problem_generator.utils import *




class TellingTimeIiProblem:
    skill_name = "telling_time_ii"
    short_description = "Telling time II."
    problem_enabled = False

    def __call__(self):
        return False



class PassingTimeWordProblemProblem:
    skill_name = "passing_time_word_problem"
    short_description = "Passing Time Word Problem."
    problem_enabled = False

    def __call__(self):
        return False



class LongDivisionWithRemainderProblem:
    skill_name = "long_division_with_remainder"
    short_description = "Long division (with remainder)."
    problem_enabled = False

    def __call__(self):
        return False



class Addition3DigitsProblem:
    skill_name = "addition_3_digits"
    short_description = "Addition (3 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class LongDivisionNoRemainderProblem:
    skill_name = "long_division_no_remainder"
    short_description = "Long division (no remainder)."
    problem_enabled = False

    def __call__(self):
        return False



class ConvertARomanNumeralToAStandardNumberProblem:
    skill_name = "convert_a_roman_numeral_to_a_standard_number"
    short_description = "Convert a Roman Numeral to a Standard Number."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleMultiplication1Or2DigitsProblem:
    skill_name = "simple_multiplication_1_or_2_digits"
    short_description = "Simple multiplication (1 or 2 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class TellingTimeIProblem:
    skill_name = "telling_time_i"
    short_description = "Telling time I."
    problem_enabled = False

    def __call__(self):
        return False



class EstimatingProductsProblem:
    skill_name = "estimating_products"
    short_description = "Estimating products."
    problem_enabled = False

    def __call__(self):
        return False



class IdentifyTheOperationWordProblemProblem:
    skill_name = "identify_the_operation_word_problem"
    short_description = "Identify the operation word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleDivisionWithZerosNoRemainderProblem:
    skill_name = "simple_division_with_zeros_no_remainder"
    short_description = "Simple division with zeros (no remainder)."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleSubtraction1Or2DigitsProblem:
    skill_name = "simple_subtraction_1_or_2_digits"
    short_description = "Simple subtraction (1 or 2 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleMultiplicationBy10XProblem:
    skill_name = "simple_multiplication_by_10x"
    short_description = "Simple multiplication (by 10x)."
    problem_enabled = False

    def __call__(self):
        return False



class PassingTimeProblem:
    skill_name = "passing_time"
    short_description = "Passing Time."
    problem_enabled = False

    def __call__(self):
        return False



class OrderOfOperationsIiProblem:
    skill_name = "order_of_operations_ii"
    short_description = "Order of operations II."
    problem_enabled = False

    def __call__(self):
        return False



class AssociativePropertyAdditionProblem:
    skill_name = "associative_property_addition"
    short_description = "Associative property (addition)."
    problem_enabled = False

    def __call__(self):
        return False



class EstimatingQuotientsProblem:
    skill_name = "estimating_quotients"
    short_description = "Estimating quotients."
    problem_enabled = False

    def __call__(self):
        return False



class EstimatingSumsProblem:
    skill_name = "estimating_sums"
    short_description = "Estimating sums."
    problem_enabled = False

    def __call__(self):
        return False



class SquareRootsProblem:
    skill_name = "square_roots"
    short_description = "Square roots."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleSubtraction1DigitProblem:
    skill_name = "simple_subtraction_1_digit"
    short_description = "Simple subtraction (1 digit)."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleSubtractionWithoutBorrowing1Or2DigitsProblem:
    skill_name = "simple_subtraction_without_borrowing_1_or_2_digits"
    short_description = "Simple subtraction without borrowing (1 or 2 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class ConvertToARomanNumeralProblem:
    skill_name = "convert_to_a_roman_numeral"
    short_description = "Convert to a Roman Numeral."
    problem_enabled = False

    def __call__(self):
        return False



class AdditionWordProblemProblem:
    skill_name = "addition_word_problem"
    short_description = "Addition word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SubtractionProblem:
    skill_name = "subtraction"
    short_description = "Subtraction."
    problem_enabled = False

    def __call__(self):
        return False



class SubtractionWordProblemProblem:
    skill_name = "subtraction_word_problem"
    short_description = "Subtraction word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleDivisionNoRemainderProblem:
    skill_name = "simple_division_no_remainder"
    short_description = "Simple division (no remainder)."
    problem_enabled = False

    def __call__(self):
        return False



class Multiplication2Or3DigitsProblem:
    skill_name = "multiplication_2_or_3_digits"
    short_description = "Multiplication (2 or 3 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class CommutativePropertyAdditionProblem:
    skill_name = "commutative_property_addition"
    short_description = "Commutative property (addition)."
    problem_enabled = False

    def __call__(self):
        return False



class OrderOfOperationsExponentsProblem:
    skill_name = "order_of_operations_exponents"
    short_description = "Order of operations (exponents)."
    problem_enabled = False

    def __call__(self):
        return False



class DivisionWordProblemProblem:
    skill_name = "division_word_problem"
    short_description = "Division word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SubtractionFrom10XProblem:
    skill_name = "subtraction_from_10x"
    short_description = "Subtraction (from 10x)."
    problem_enabled = False

    def __call__(self):
        return False



class RoundingProblem:
    skill_name = "rounding"
    short_description = "Rounding."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleAddition1DigitProblem:
    skill_name = "simple_addition_1_digit"
    short_description = "Simple addition (1 digit)."
    problem_enabled = False

    def __call__(self):
        return False



class EstimatingDifferencesProblem:
    skill_name = "estimating_differences"
    short_description = "Estimating differences."
    problem_enabled = False

    def __call__(self):
        return False



class PlaceValuesWholeNumbersProblem:
    skill_name = "place_values_whole_numbers"
    short_description = "Place values (Whole Numbers)."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleDivisionWithRemainderProblem:
    skill_name = "simple_division_with_remainder"
    short_description = "Simple division (with remainder)."
    problem_enabled = False

    def __call__(self):
        return False



class WriteNumberInExpandedFormProblem:
    skill_name = "write_number_in_expanded_form"
    short_description = "Write number in expanded form."
    problem_enabled = False

    def __call__(self):
        return False



class SimplifyingExpandedFormProblem:
    skill_name = "simplifying_expanded_form"
    short_description = "Simplifying expanded form."
    problem_enabled = False

    def __call__(self):
        return False



class MultiplicationWordProblemProblem:
    skill_name = "multiplication_word_problem"
    short_description = "Multiplication word problem."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleMultiplicationIiProblem:
    skill_name = "simple_multiplication_ii"
    short_description = "Simple multiplication II."
    problem_enabled = False

    def __call__(self):
        return False



class SimpleAddition12DigitsProblem:
    skill_name = "simple_addition_1_2_digits"
    short_description = "Simple addition (1 - 2 digits)."
    problem_enabled = False

    def __call__(self):
        return False



class ConvertBetweenPlaceValuesProblem:
    skill_name = "convert_between_place_values"
    short_description = "Convert between place values."
    problem_enabled = False

    def __call__(self):
        return False



class OrderOfOperationsProblem:
    skill_name = "order_of_operations"
    short_description = "Order of operations."
    problem_enabled = False

    def __call__(self):
        return False


