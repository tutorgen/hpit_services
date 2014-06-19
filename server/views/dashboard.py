import os
from uuid import uuid4

from flask import request, render_template, redirect, url_for
from flask.ext.user import login_required, current_user

from server import app, db, HPIT_STATUS
from server.models import Plugin, Tutor
from server.forms import PluginForm, TutorForm

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


@app.route('/plugins')
@login_required
def plugins():
    """
    SUPPORTS: GET
    Shows a user's plugins.
    """
    plugins = current_user.plugins

    return render_template('plugins.html', plugins=plugins)


@app.route('/plugin/new', methods=["GET", "POST"])
@login_required
def plugin_new():
    """
    SUPPORTS: GET, POST
    Allows the user to create a new plugin.
    """

    plugin_form = PluginForm(request.form)

    if request.method == "POST":
        if plugin_form.validate():
            new_plugin = Plugin()
            plugin_form.populate_obj(new_plugin)
            new_plugin.user = current_user

            new_plugin.entity_id = str(uuid4())
            key = new_plugin.generate_key()

            db.session.add(new_plugin)
            db.session.commit()

            return render_template('plugin_key.html', plugin=new_plugin, key=key)

    return render_template('plugin_new.html', form=plugin_form)


@app.route('/plugin/edit/<plugin_id>', methods=["GET", "POST"])
@login_required
def plugin_edit(plugin_id):
    """
    SUPPORTS: GET, POST
    Allows the user to edit a plugin
    """

    plugin = Plugin.query.get(plugin_id)

    if plugin.user != current_user:
        abort(403)

    plugin_form = PluginForm(request.form, plugin)

    if request.method == "POST":
        if plugin_form.validate():
            plugin_form.populate_obj(plugin)

            db.session.add(plugin)
            db.session.commit()

            return redirect(url_for('plugins'))

    return render_template('plugin_edit.html', form=plugin_form)


@app.route('/plugin/genkey/<plugin_id>', methods=["GET"])
@login_required
def plugin_genkey(plugin_id):
    """
    SUPPORTS: GET
    Allows the user to generate a new API key for their plugin.
    """

    plugin = Plugin.query.get(plugin_id)

    if plugin.user != current_user:
        abort(403)

    key = plugin.generate_key()

    db.session.add(plugin)
    db.session.commit()

    return render_template('plugin_key.html', plugin=plugin, key=key)


@app.route('/plugin/delete/<plugin_id>', methods=["GET"])
@login_required
def plugin_delete(plugin_id):
    """
    SUPPORTS: GET
    Allows the user to delete a plugin
    """

    plugin = Plugin.query.get(plugin_id)

    if plugin.user != current_user:
        abort(403)

    db.session.delete(plugin)
    db.session.commit()

    return redirect(url_for('plugins'))


@app.route('/tutors')
@login_required
def tutors():
    """
    SUPPORTS: GET
    Shows a user's tutors.
    """
    tutors = current_user.tutors

    return render_template('tutors.html', tutors=tutors)


@app.route('/tutor/new', methods=["GET", "POST"])
@login_required
def tutor_new():
    """
    SUPPORTS: GET, POST
    Allows the user to create a new plugin.
    """

    tutor_form = TutorForm(request.form)

    if request.method == "POST":
        if tutor_form.validate():
            new_tutor = Tutor()
            tutor_form.populate_obj(new_tutor)
            new_tutor.user = current_user

            new_tutor.entity_id = str(uuid4())
            key = new_tutor.generate_key()

            db.session.add(new_tutor)
            db.session.commit()

            return render_template('tutor_key.html', tutor=new_tutor, key=key)

    return render_template('tutor_new.html', form=tutor_form)


@app.route('/tutor/edit/<tutor_id>', methods=["GET", "POST"])
@login_required
def tutor_edit(tutor_id):
    """
    SUPPORTS: GET, POST
    Allows the user to edit a plugin
    """

    tutor = Tutor.query.get(tutor_id)

    if tutor.user != current_user:
        abort(403)

    tutor_form = TutorForm(request.form, tutor)

    if request.method == "POST":
        if tutor_form.validate():
            tutor_form.populate_obj(tutor)

            db.session.add(tutor)
            db.session.commit()

            return redirect(url_for('tutors'))

    return render_template('tutor_edit.html', form=tutor_form)


@app.route('/tutor/genkey/<tutor_id>', methods=["GET"])
@login_required
def tutor_genkey(tutor_id):
    """
    SUPPORTS: GET
    Allows the user to generate a new API key for their plugin.
    """

    tutor = Tutor.query.get(tutor_id)

    if tutor.user != current_user:
        abort(403)

    key = tutor.generate_key()

    db.session.add(tutor)
    db.session.commit()

    return render_template('tutor_key.html', tutor=tutor, key=key)




@app.route('/tutor/delete/<tutor_id>', methods=["GET"])
@login_required
def tutor_delete(tutor_id):
    """
    SUPPORTS: GET
    Allows the user to delete a plugin
    """
    tutor = Tutor.query.get(tutor_id)

    if tutor.user != current_user:
        abort(403)

    db.session.delete(tutor)
    db.session.commit()

    return redirect(url_for('tutors'))
