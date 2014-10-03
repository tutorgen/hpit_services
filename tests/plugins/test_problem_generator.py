import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from plugins import ProblemGeneratorPlugin

class TestProblemGeneratorPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ProblemGeneratorPlugin(123,456,None)
        self.test_subject.problem_library = {
            'arithmetic': {
                'addition': {
                    'AddTwoTwoDigitNumbers': lambda: ('problem', 'answer'),
                },
            }
        }
        self.test_subject.update_problem_list()


    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None



    def test_list_problems_callback_no_subject(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - No Subject
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
        })
        self.test_subject.send_response.assert_called_with("1", {
            'arithmetic': {
                'addition': ['AddTwoTwoDigitNumbers']
            }
        })


    def test_list_problems_callback_invalid_subject(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - Invalid Subject
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "algebra_1"
        })
        self.test_subject.send_response.assert_called_with("1", {
            'send': {
                'subjects': ['arithmetic']
            }, 
            'error': 'Subject <algebra_1> does not exist.'
        })


    def test_list_problems_callback_no_category(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - No Category
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "arithmetic"
        })
        self.test_subject.send_response.assert_called_with("1", {
            'arithmetic': {
                'addition': ['AddTwoTwoDigitNumbers']
            }
        })


    def test_list_problems_callback_invalid_category(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - Invalid Category
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "arithmetic",
            'category': "multiples"
        })
        self.test_subject.send_response.assert_called_with("1", {
            'send': {
                'categories': ['addition']
            }, 'error': 'Category <multiples> does not exist in subject <arithmetic>'
        })


    def test_list_problems_callback_no_skill(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - No Skill
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "arithmetic",
            'category': "addition"
        })
        self.test_subject.send_response.assert_called_with("1", {
            'arithmetic': {
                'addition': ['AddTwoTwoDigitNumbers']
            }
        })


    def test_list_problems_callback_invalid_skill(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - Invalid Skill
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "arithmetic",
            'category': "addition",
            'skill': 'multiples'

        })
        self.test_subject.send_response.assert_called_with("1", {
            'send': {
                'skills': ['AddTwoTwoDigitNumbers']
            }, 'error': 'Skill <multiples> does not exist in subject <arithmetic> and category <addition>'
        })


    def test_list_problems_callback_valid_sub_cat_skill(self):
        """
        ProblemGeneratorPlugin.list_problems_callback() Test - Valid Subject, Category, Skill
        """
        self.test_subject.send_response = MagicMock()

        self.test_subject.list_problems_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': "arithmetic",
            'category': "addition",
            'skill': 'AddTwoTwoDigitNumbers'
        })
        self.test_subject.send_response.assert_called_with("1", {
            'arithmetic': {
                'addition': ['AddTwoTwoDigitNumbers']
            }
        })


    def test_generate_problem_callback(self):
        """
        ProblemGeneratorPlugin.generate_problem_callback() Test - No Subject
        """
        self.test_subject.send_response = MagicMock()
        self.test_subject.generate_problem = MagicMock(return_value={})
        self.test_subject.generate_problem_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
        })

        self.test_subject.generate_problem.assert_called_with('arithmetic', "addition", "AddTwoTwoDigitNumbers")


    def test_generate_problem_callback_with_count(self):
        """
        ProblemGeneratorPlugin.generate_problem_callback() Test - With Count Parameter
        """
        self.test_subject.send_response = MagicMock()
        self.test_subject.generate_problem = MagicMock(return_value={})

        self.test_subject.generate_problem_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'count': 2
        })

        (self.test_subject.generate_problem.call_count).should.be(2)


    def test_generate_problem_callback_with_options(self):
        """
        ProblemGeneratorPlugin.generate_problem_callback() Test - With Options
        """
        self.test_subject.send_response = MagicMock()
        self.test_subject.generate_problem = MagicMock(return_value={})
        self.test_subject.generate_problem_callback({
            'message_id': "1",
            'sender_entity_id': "2",
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'options': {'thing': 1}
        })

        self.test_subject.generate_problem.assert_called_with('arithmetic', "addition", "AddTwoTwoDigitNumbers", thing=1)


    def test_generate_problem_no_subject(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - No Subject
        """
        self.test_subject.generate_problem.when.called_with(
            None, 'addition', 'AddTwoTwoDigitNumbers').should.return_value({
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'problem_text': 'problem',
            'answer_text': 'answer'
        })


    def test_generate_problem_invalid_subject(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - Invalid Subject
        """
        self.test_subject.generate_problem.when.called_with(
            'invalid', 'addition', 'AddTwoTwoDigitNumbers').should.throw(Exception)


    def test_generate_problem_no_category(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - No Category
        """
        self.test_subject.generate_problem.when.called_with(
            'arithmetic', None, 'AddTwoTwoDigitNumbers').should.return_value({
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'problem_text': 'problem',
            'answer_text': 'answer'
        })


    def test_generate_problem_invalid_category(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - Invalid Category
        """
        self.test_subject.generate_problem.when.called_with(
            'arithmetic', 'invalid', 'AddTwoTwoDigitNumbers').should.throw(Exception)


    def test_generate_problem_no_skill(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - No Skill
        """
        self.test_subject.generate_problem.when.called_with(
            'arithmetic', 'addition', None).should.return_value({
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'problem_text': 'problem',
            'answer_text': 'answer'
        })


    def test_generate_problem_invalid_skill(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - Invalid Skill
        """
        self.test_subject.generate_problem.when.called_with(
            'arithmetic', 'addition', 'invalid').should.throw(Exception)


    def test_generate_problem_valid_subject_category_skill(self):
        """
        ProblemGeneratorPlugin.generate_problem() Test - Valid Subject, Category & Skill
        """
        self.test_subject.generate_problem.when.called_with(
            'arithmetic', 'addition', 'AddTwoTwoDigitNumbers').should.return_value({
            'subject': 'arithmetic',
            'category': 'addition',
            'skill': 'AddTwoTwoDigitNumbers',
            'problem_text': 'problem',
            'answer_text': 'answer'
        })

