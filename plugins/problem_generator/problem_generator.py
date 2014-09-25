import os
import inspect
import importlib
import pkgutil
import types
import random
from plugins.problem_generator import problems

from hpitclient import Plugin

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class ProblemGeneratorPlugin(Plugin):

    def __init__(self, *args, **kwargs):
        self.load_problem_library()
        super().__init__(*args, **kwargs)


    def load_problem_library(self):
        self.problem_library = {}
        root_directory = os.path.dirname(problems.__file__)

        for dirpath, dirnames, filenames in os.walk(root_directory):
            if dirpath.endswith('__pycache__'):
                continue

            filenames = [fn for fn in filenames if fn != '__init__.py']

            if not filenames:
                continue

            for fn in filenames:
                import_path = dirpath.replace(os.getcwd(),'')[1:].split('/')

                category_name = fn.split('.')[0]
                subject_name = import_path[-1]
                import_path.append(category_name)

                imported = importlib.import_module('.'.join(import_path))

                functions = {
                    attr: getattr(imported, attr, None) 
                        for attr in dir(imported) if attr.endswith('Problem')
                }

                if subject_name not in self.problem_library:
                    self.problem_library[subject_name] = {}

                subject_dict = self.problem_library[subject_name]
                subject_dict[category_name] = functions


    def generate_problem(self, subject=None, category=None, skill=None, **kwargs):
        if subject is None:
            subject = random.choice(list(self.problem_library.keys()))
        elif subject not in self.problem_library:
            raise Exception("Subject is invalid.")

        subject_obj = self.problem_library[subject]

        if category is None:
            category = random.choice(list(subject_obj.keys()))
        elif category not in subject_obj:
            raise Exception("Category is invalid.")

        category_obj = subject_obj[category]

        if skill is None:
            skill = random.choice(list(category_obj.keys()))
        elif skill not in category_obj:
            raise Exception("Skill is invalid.")

        skill_obj = category_obj[skill]

        problem_text, answer_text = skill_obj(**kwargs)

        return {
            'subject': subject,
            'category': category,
            'skill': skill,
            'problem_text': problem_text,
            'answer_text': answer_text
        }


    def post_connect(self):
        super().post_connect()

        self.subscribe(
            pg_list_problems=self.list_problems,
            pg_generate_problem=self.generate_problem)


    def list_problems(self):
        pass


    def generate_problem(self):
        pass