import os

from flask import render_template
from flask.ext.user import login_required

from server import app, HPIT_STATUS

@app.route("/")
def index():
    """
    SUPPORTS: GET
    Shows the main page for HPIT.
    """
    return render_template('index.html', 
        tutor_count=len(HPIT_STATUS['tutors']),
        plugin_count=len(HPIT_STATUS['plugins']),
        tutors=HPIT_STATUS['tutors'],
        plugins=HPIT_STATUS['plugins']
    )

def documentation_markdown():
    if not documentation_markdown.docs_read:
        with open(os.path.join(os.getcwd(), 'server/assets/docs.md'), 'r') as f:
            documentation_markdown.markdown = f.read()
        documentation_markdown.docs_read = True

    return documentation_markdown.markdown
documentation_markdown.docs_read = False

@app.route("/docs")
def docs():
    """
    SUPPORTS: GET
    Shows the API documentation for HPIT.
    """
    doc_markdown = documentation_markdown()
    return render_template('docs.html', docs=doc_markdown)

@app.route("/routes")
def routes():
    """
    SUPPORTS: GET
    Shows the routes documentation for HPIT (generated).
    """
    links = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            docs = app.view_functions[rule.endpoint].__doc__

            if docs:
                docs = docs.replace('\n', '<br/>')

            links.append((rule.rule, docs))

    return render_template('routes.html', 
        links=links)
