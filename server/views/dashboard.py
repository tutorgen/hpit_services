from flask import render_template
from flask.ext.user import login_required

from server import app, HPIT_STATUS

@login_required
@app.route("/")
def index():
    """
    SUPPORTS: GET
    Shows the status dashboard and API route links for HPIT.
    """
    links = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            docs = app.view_functions[rule.endpoint].__doc__

            if docs:
                docs = docs.replace('\n', '<br/>')

            links.append((rule.rule, docs))

    return render_template('index.html', 
        links=links, 
        tutor_count=len(HPIT_STATUS['tutors']),
        plugin_count=len(HPIT_STATUS['plugins']),
        tutors=HPIT_STATUS['tutors'],
        plugins=HPIT_STATUS['plugins']
    )
