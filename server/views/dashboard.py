import os
from uuid import uuid4

from flask import request, render_template
from flask.ext.user import login_required, current_user

from server import app, HPIT_STATUS
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


@app.route('/plugin/<entity_id>')
@login_required
def plugin_detail(entity_id):
    plugin = Plugin.query.filter(user_id=current_user.id, entity_id=entity_id).first_or_404()

    if plugin.user_id != current_user.id:
        return abort(403)

    return render_template('plugin_detail.html', plugin=plugin)


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

            new_plugin.entity_id = uuid4()
            key = new_plugin.generate_key()

            return render_template('plugin_key.html', plugin=new_plugin, key=key)

    return render_template('plugin_new.html', form=plugin_form)


@app.route('/plugin/edit/<entity_id>', methods=["GET", "POST"])
@login_required
def plugin_edit(entity_id):
    """
    SUPPORTS: GET, POST
    Allows the user to edit a plugin
    """

    plugin = Plugin.query.filter(user_id=current_user.id, entity_id=entity_id).first_or_404()

    plugin_form = PluginForm(request.POST, plugin)

    if request.method == "POST":
        if form.validate():
            plugin_form.populate_obj(plugin)

            return redirect(url_for('plugin_detail', entity_id))

    return render_template('plugin_edit.html', form=plugin_form, plugin=plugin)


@app.route('/plugin/delete/<entity_id>', methods=["POST"])
@login_required
def plugin_delete():
    """
    SUPPORTS: POST
    Allows the user to delete a plugin
    """

    plugin = Plugin.query.filter(user_id=current_user.id, entity_id=entity_id).first_or_404()
    plugin.delete()

    return redirect(url_for('plugins'))


@app.route('/tutors')
@login_required
def tutors():
    """
    SUPPORTS: GET
    Shows a user's tutors.
    """

    return render_template('tutors.html')


@app.route('/tutor/new', methods=["GET", "POST"])
@login_required
def tutor_new():
    """
    SUPPORTS: GET, POST
    Allows the user to create a new plugin.
    """

    return render_template('tutor_new.html')


@app.route('/tutor/edit', methods=["GET", "POST"])
@login_required
def tutor_edit():
    """
    SUPPORTS: GET, POST
    Allows the user to edit a plugin
    """

    return render_template('tutor_edit.html')


@app.route('/tutor/delete', methods=["POST"])
@login_required
def tutor_delete():
    """
    SUPPORTS: POST
    Allows the user to delete a plugin
    """

    return render_template('tutor_edit.html')

