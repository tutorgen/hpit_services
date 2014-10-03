import json
from markdown import markdown
from flask import Flask, request, render_template, jsonify, abort
from utils import load_problem_data, load_readme
from generator import ProblemGenerator

app = Flask(__name__)

README = load_readme()
APP_DATA = load_problem_data()
generator = ProblemGenerator(APP_DATA)


@app.route("/")
def index():
    return render_template('index.html', readme=README)


@app.route("/todo")
def todo():

    todo_data = []
    for sub_name, subject in APP_DATA.items():
        for cat_name, category in subject['categories'].items():
            if not all([sk['enabled'] for sk in category['skills'].values()]):
                todo_data.append({
                    'subject': sub_name, 
                    'category': cat_name, 
                    'points': len(category['skills']) * 2
                })

    return jsonify({'todo': todo_data})


@app.route("/all")
def all_list():
    return jsonify(generator.enabled_data)


@app.route("/list")
def subject_list():
    return jsonify({'subjects': [name for name in generator.enabled_data.keys()]})


@app.route("/<subject>/new")
def subject_new(subject=None):
    if subject not in generator.enabled_data or subject is None:
        abort(404)

    subject = generator.enabled_data[subject]

    return jsonify({})


@app.route("/<subject>/list")
def subject_category_list(subject=None):
    if subject not in generator.enabled_data or subject is None:
        abort(404)

    subject = generator.enabled_data[subject]

    return jsonify({'categories': [name for name in subject['categories'].keys()]})


@app.route("/<subject>/<category>/new")
def subject_category_new(subject=None, category=None):
    return jsonify({})


@app.route("/<subject>/<category>/list")
def subject_category_skill_list(subject=None, category=None):
    if subject not in generator.enabled_data or subject is None or category is None:
        abort(404)

    subject = generator.enabled_data[subject]

    if category not in subject['categories']:
        abort(404)

    category = subject['categories'][category]

    return jsonify({'skills': [name for name in category['skills'].keys()]})


@app.route("/<subject>/<category>/<skill>/new")
def subject_category_skill_new(subject=None, category=None, skill=None):
    if subject not in generator.enabled_data or subject is None or category is None:
        abort(404)

    request_args = dict(request.args)

    count = 1
    if 'count' in request.args:
        count = int(request.args['count'])
        del request_args['count']

    problems = []
    for i in range(0, count):
        problems.append(generator.generate_problem(subject, category, skill, **request_args))

    return jsonify({
        'problems': problems
        })


if __name__ == "__main__":
    app.run(debug=True)