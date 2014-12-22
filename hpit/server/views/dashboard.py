import os
from datetime import datetime, timedelta
from uuid import uuid4

from flask import request, render_template, redirect, url_for
from flask.ext.user import login_required, current_user

from hpit.server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
db = app_instance.db
mongo = app_instance.mongo
csrf = app_instance.csrf

from hpit.server.models import Plugin, Tutor
from hpit.server.forms import PluginForm, TutorForm

#for the student monitor
from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()
from pymongo import MongoClient
from bson.objectid import ObjectId
import bson
#-----------------------------

def query_metrics(collection, metric_name, senders=None, receivers=None):
    end = datetime.now()

    def _query_metrics_with_time(time_delta):
        query_count = None

        if senders and receivers:
            query_count = collection.find({
                metric_name: {'$gte': end - time_delta, '$lt': end },
                '$or' : [
                    {
                        'sender_entity_id': {
                            '$in' : senders
                        }
                    }, {
                        'receiver_entity_id': {
                            '$in': receivers
                        }
                    }
                ] 
            }).count()
        elif senders:
            query_count = collection.find({
                metric_name: {'$gte': end - time_delta, '$lt': end },
                'sender_entity_id': {'$in' : senders},
            }).count()
        elif receivers:
            query_count = collection.find({
                metric_name: {'$gte': end - time_delta, '$lt': end },
                'receiver_entity_id': {'$in': receivers},
            }).count()
        else:
            query_count = collection.find({
                metric_name: {'$gte': end - time_delta, '$lt': end }
            }).count()

        return query_count

    seconds = _query_metrics_with_time(timedelta(seconds=1))
    minutes = _query_metrics_with_time(timedelta(minutes=1))
    hours = _query_metrics_with_time(timedelta(hours=1))
    days = _query_metrics_with_time(timedelta(days=1))

    return (seconds, minutes, hours, days)


@app.route("/")
def index():
    """
    SUPPORTS: GET
    Shows the main page for HPIT.
    """
    active_poll_time = datetime.now() - timedelta(minutes=3)

    plugins = list(Plugin.query.filter(Plugin.time_last_polled >= active_poll_time))
    tutors = list(Tutor.query.filter(Tutor.time_last_polled >= active_poll_time))

    messages_created = query_metrics(mongo.db.plugin_messages, 'time_created')
    messages_received = query_metrics(mongo.db.sent_messages_and_transactions, 'time_received')
    responses_created = query_metrics(mongo.db.sent_messages_and_transactions, 'time_responded')
    responses_received = query_metrics(mongo.db.sent_responses, 'time_response_received')

    return render_template('index.html', 
        tutor_count=len(tutors),
        plugin_count=len(plugins),
        tutors=tutors,
        plugins=plugins,
        messages_created=messages_created,
        messages_received=messages_received,
        responses_created=responses_created,
        responses_received=responses_received
    )


@app.route("/docs")
def docs():
    """
    SUPPORTS: GET
    Shows the API documentation for HPIT.
    """
    return render_template('docs.html')


@app.route("/client-docs")
def client_docs():
    """
    SUPPORTS: GET
    Shows the Python Client Documentation
    """
    return render_template('client_docs.html')


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
    
    connected_dict = {}
    for p in plugins:
        active_poll_time = datetime.now() - timedelta(minutes=1)
        if p.time_last_polled >= active_poll_time:
            connected_dict[p.id] = True
        else:
            connected_dict[p.id] = False
        

    return render_template('plugins.html', plugins=plugins,connected_dict=connected_dict)


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

    return render_template('plugin_new.html', form=plugin_form, isadmin=current_user.administrator)


@app.route('/plugin/<plugin_id>/detail', methods=["GET"])
@login_required
def plugin_detail(plugin_id):
    """
    SUPPORTS: GET, POST
    Allows the user to view a plugin's details
    """
    plugin = Plugin.query.get(plugin_id)

    if plugin.user != current_user:
        abort(403)

    log_entries = mongo.db.entity_log.find({
        'entity_id': plugin.entity_id,
        'deleted': False
    })

    return render_template('plugin_detail.html', plugin=plugin, logs=log_entries)


@app.route('/plugin/<plugin_id>/log/clear', methods=["GET"])
@login_required
def plugin_clear_log(plugin_id):
    """
    SUPPORTS: GET, POST
    Allows the user to view a plugin's details
    """
    plugin = Plugin.query.get(plugin_id)

    if plugin.user != current_user:
        abort(403)

    mongo.db.entity_log.update(
        {'entity_id': plugin.entity_id, 'deleted': False},
        {"$set": {'deleted':True}}, 
        multi=True
    )

    return redirect(''.join(['/plugin/', plugin_id, '/detail']))


@app.route('/plugin/<plugin_id>/edit', methods=["GET", "POST"])
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

    return render_template('plugin_edit.html', form=plugin_form, isadmin=current_user.administrator)


@app.route('/plugin/<plugin_id>/genkey', methods=["GET"])
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


@app.route('/plugin/<plugin_id>/delete', methods=["GET"])
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
    
    connected_dict = {}
    for t in tutors:
        active_poll_time = datetime.now() - timedelta(minutes=1)
        if t.time_last_polled >= active_poll_time:
            connected_dict[t.id] = True
        else:
            connected_dict[t.id] = False

    return render_template('tutors.html', tutors=tutors,connected_dict=connected_dict)


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


@app.route('/tutor/<tutor_id>/detail', methods=["GET"])
@login_required
def tutor_detail(tutor_id):
    """
    SUPPORTS: GET, POST
    Allows the user to view a tutor's details
    """
    tutor = Tutor.query.get(tutor_id)

    if tutor.user != current_user:
        abort(403)

    log_entries = mongo.db.entity_log.find({
        'entity_id': tutor.entity_id,
        'deleted': False
    })

    return render_template('tutor_detail.html', tutor=tutor, logs=log_entries)

    
@app.route('/tutor/<tutor_id>/log/clear', methods=["GET"])
@login_required
def tutor_clear_log(tutor_id):
    """
    SUPPORTS: GET, POST
    Allows the user to clear the tutor's logs
    """
    tutor = Tutor.query.get(tutor_id)

    if tutor.user != current_user:
        abort(403)

    mongo.db.entity_log.update(
        {'entity_id': tutor.entity_id, 'deleted': False},
        {"$set": {'deleted':True}}, 
        multi=True
    )

    return redirect(''.join(['/tutor/', tutor_id, '/detail']))


@app.route('/tutor/<tutor_id>/edit', methods=["GET", "POST"])
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


@app.route('/tutor/<tutor_id>/genkey', methods=["GET"])
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


@app.route('/tutor/<tutor_id>/delete', methods=["GET"])
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


@app.route('/account/company', methods=["POST"])
@login_required
def account_company():
    """
    SUPPORTS: PUT
    Updates the currently loggest in user's company.
    """
    new_company_name = request.form['company']

    if not new_company_name:
        return render_template('account_detail.html', error="Your company cannot be empty.")

    current_user.company = new_company_name
    db.session.add(current_user)
    db.session.commit()
    
    
    return redirect("/account")
    #return render_template('account_detail.html', flash='Your company was updated successfully!')


@app.route('/account', methods=["GET"])
@login_required
def account_details():
    """
    SUPPORTS: GET
    Shows the currently logged in user's account details.
    """
    plugins = current_user.plugins
    tutors = current_user.tutors

    active_poll_time = datetime.now() - timedelta(minutes=15)

    active_plugins = list(filter(lambda x: x.time_last_polled >= active_poll_time, plugins))
    active_tutors = list(filter(lambda x: x.time_last_polled >= active_poll_time, tutors))

    senders = list(map(lambda x: x.entity_id, tutors))
    receivers = list(map(lambda x: x.entity_id, plugins))

    messages_created = query_metrics(mongo.db.plugin_messages, 'time_created', senders, receivers)
    messages_received = query_metrics(mongo.db.sent_messages_and_transactions, 'time_received', senders, receivers)
    responses_created = query_metrics(mongo.db.sent_messages_and_transactions, 'time_responded', senders, receivers)
    responses_received = query_metrics(mongo.db.sent_responses, 'time_response_received', senders, receivers)

    return render_template('account_detail.html', 
        tutor_count=len(active_tutors),
        plugin_count=len(active_plugins),
        tutors=active_tutors,
        plugins=active_plugins,
        messages_created=messages_created,
        messages_received=messages_received,
        responses_created=responses_created,
        responses_received=responses_received
    )

@csrf.exempt
@app.route('/student-monitor',methods=["GET","POST"])
@login_required
def student_monitor(student_id=""):
    if request.method == 'POST':
        #student_attributes = {"name":"brian","interests":["sports","music","plants"]}
        student_skills = [
            {"skill_name":"Addition",
             "skill_id":"1",
             "prob_known":.45,
             "prob_learned":.32,
             "prob_mistake":.20,
             "prob_guess":.56,
           },
           {"skill_name":"Subtraction",
             "skill_id":"1",
             "prob_known":.6,
             "prob_learned":.92,
             "prob_mistake":.60,
             "prob_guess":.31,
           },
        ]
        student_problems = [
            {"problem_name":"Area of a door",
             "problem_id":"p123",
             "number_of_steps":"4",
             "skills_involved":["addition","reading","some other skill"],
            },
            {"problem_name":"Angles problem",
             "problem_id":"p1235",
             "number_of_steps":"6",
             "skills_involved":["baseball","eating contest","skydiving"],
            }
           
        ]
        bored=True
        
        """
        This is basically a hack.  The dashboard should not have access to the plugin's databases.
        In the future, the dashboard should send messages, just as other plugins do.
        """
        
        def error_template(msg):
            return render_template('student_monitor_detail.html',
                  student_id=request.form["student_id"],
                  error=msg,
                  student_attributes={},
                  student_skills=[],
                  student_problems=[],
                  bored=False,      
                )
        
        mongo = MongoClient(settings.MONGODB_URI)
        
        #student_id
        student_id = request.form["student_id"]
        
        #error message
        error = None
        
        #student_attributes
        student_attributes = {}
        db = mongo[settings.MONGO_DBNAME].hpit_students
        
        try:
            student = db.find_one({"_id":ObjectId(str(student_id))})
            if not student:
                return error_template("Could not find student with ID " + str(student_id))
            for item in student["attributes"]:
                student_attributes[item] = student["attributes"][item]
        
        except bson.errors.InvalidId:
            return error_template("Invalid student id.")
        
        #student_skills
        student_skills = []
        skill_db = mongo[settings.MONGO_DBNAME].hpit_skills
        kt_db = mongo[settings.MONGO_DBNAME].hpit_knowledge_tracing
        kts = kt_db.find({"student_id":str(student_id)})
        for kt in kts:
            skill = skill_db.find_one({"_id":ObjectId(kt["skill_id"])})
            if not skill:
                skill_name = "unknown"
                skill_model = "unknown"
            else:
                skill_name = skill["skill_name"]
                skill_model = skill["skill_model"]
                
            student_skills.append(
                {"skill_name":skill_name,
                 "skill_id":kt["skill_id"],
                 "skill_model":skill_model,
                 "prob_known":kt["probability_known"],
                 "prob_learned":kt["probability_learned"],
                 "prob_mistake":kt["probability_mistake"],
                 "prob_guess":kt["probability_guess"],
               })
            
        
        
        return render_template('student_monitor_detail.html',
              student_id=request.form["student_id"],
              error=error,
              student_attributes=student_attributes,
              student_skills=student_skills,
              student_problems=student_problems,
              bored=bored,      
        )
    else:
        return render_template('student_monitor.html')

