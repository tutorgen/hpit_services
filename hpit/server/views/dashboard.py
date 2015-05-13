import os
from datetime import datetime, timedelta
from uuid import uuid4

from flask import request, render_template, redirect, url_for, jsonify
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
import pymongo
import math
#-----------------------------

#for the message tracker
server_settings = SettingsManager.get_server_settings()

class PluginCommunication(object):
    def __init__(self,plugin_id,hpit_received,plugin_received,plugin_responded,response_received):
        self.plugin_id = plugin_id
        self.plugin_received = plugin_received
        self.plugin_responded = plugin_responded
        self.response_received = response_received
        
        self.plugin_received_dt = plugin_received - hpit_received
        
        self.plugin_used = False
        self.plugin_responded_dt = None
        self.response_received_dt = None
        if plugin_responded:
            self.plugin_responded_dt = plugin_responded - plugin_received
            if response_received:
                self.plugin_used = True
                self.response_received_dt = response_received - plugin_responded
                self.total_time = self.plugin_received_dt + self.plugin_responded_dt + self.response_received_dt
            else:
                self.total_time = self.plugin_received_dt + self.plugin_responded_dt
        else:
             self.total_time = self.plugin_received_dt
            
class MessageTimes(object):
    def __init__(self,message_id):
        self.hpit_received = None
        self.plugin_communications = []

        self.message_name = None        
        self.message_id = message_id
        
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo[server_settings.MONGO_DBNAME]
        
    def get(self): #used for message tracking
        orig_message = self.db.messages_and_transactions.find_one({"_id":ObjectId(self.message_id)})
        self.hpit_received = orig_message["time_created"].replace(tzinfo=None)
        self.message_name = orig_message["message_name"]
        self.get_plugin_connections()
    
    def get_from_existing_query(self,time_created,message_name):
        self.hpit_received = time_created.replace(tzinfo=None)
        self.message_name = message_name
        self.get_plugin_connections()
        
    def get_plugin_connections(self):
        messages_received_by_plugins = self.db.sent_messages_and_transactions.find({"message_id":ObjectId(self.message_id)})
        for message in messages_received_by_plugins:
            time_responded = None
            time_response_received = None
            if "time_responded" in message:
                time_responded = message["time_responded"]
                response = self.db.sent_responses.find_one({"message_id":ObjectId(message["message_id"]),"receiver_entity_id":message["sender_entity_id"]})
                if response:
                    time_response_received = response["time_response_received"]
            plugin_communication = PluginCommunication(message["receiver_entity_id"],self.hpit_received,message["time_received"],time_responded,time_response_received)
            self.plugin_communications.append(plugin_communication)
            
        
    def get_child_messages(self,mid):
        ids = []
        child_messages = self.db.messages_and_transactions.find({"payload._seed_message_id":mid})
        for c in child_messages:
            ids.append(str(c["_id"]))
            ids = ids + self.get_child_messages(str(c["_id"]))
            
        return ids
    


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

    plugins = list(Plugin.query.filter(Plugin.connected == True))
    tutors = list(Tutor.query.filter(Tutor.connected == True))

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
        if p.connected == True:
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
            
            connected_dict = {new_plugin.entity_id:False}

            return render_template('plugin_key.html', plugin=new_plugin, key=key, connected_dict=connected_dict)

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

    connected_dict = {}
    if plugin.connected == True:
        connected_dict[plugin.id] = True
    else:
        connected_dict[plugin.id] = False

    return render_template('plugin_detail.html', plugin=plugin, logs=log_entries, connected_dict=connected_dict)


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
    
    connected_dict = {plugin.entity_id:False}

    return render_template('plugin_key.html', plugin=plugin, key=key, connected_dict=connected_dict)


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
        if t.connected == True:
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
            
            connected_dict = {new_tutor.entity_id:False}

            return render_template('tutor_key.html', tutor=new_tutor, key=key, connected_dict = connected_dict)

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

    connected_dict = {}
    if tutor.connected == True:
        connected_dict[tutor.id] = True
    else:
        connected_dict[tutor.id] = False
    
    return render_template('tutor_detail.html', tutor=tutor, logs=log_entries, connected_dict=connected_dict)

    
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
    
    connected_dict = {tutor.entity_id:False}

    return render_template('tutor_key.html', tutor=tutor, key=key, connected_dict=connected_dict)


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

    active_plugins = list(filter(lambda x: x.connected == True, plugins))
    active_tutors = list(filter(lambda x: x.connected == True, tutors))

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
            
        #student_problems
        student_problems = []
        problem_worked_db = mongo[settings.MONGO_DBNAME].hpit_problems_worked
        problem_db = mongo[settings.MONGO_DBNAME].hpit_problems
        step_db = mongo[settings.MONGO_DBNAME].hpit_steps
        
        problems_worked = problem_worked_db.find({"student_id":str(student_id)})
        for problem in problems_worked:
            actual_problem = problem_db.find_one({"_id":problem["problem_id"]})
            step_count = 0
            skill_list = []
            steps = step_db.find({"problem_id":problem["problem_id"]})
            for step in steps:
                for skill in step["skill_names"]:
                    skill_list.append(skill)
                step_count +=1
                
            student_problems.append({
                "problem_name":actual_problem["problem_name"],
                "problem_id":str(problem["_id"]),
                "number_of_steps":step_count,
                "skills_involved":skill_list,
            })
        
        #boredom (straight from boredom_detector.boredom_calculation())
        bored = False
        
        boredom_db = mongo[settings.MONGO_DBNAME].hpit_boredom_detection
        dt_sum = 0
        dt_mean = 0
        dt_std_dev = 0
        dts = []
        
        records = list(boredom_db.find({"student_id":student_id},limit=1000).sort("time",pymongo.DESCENDING))
        if len(records) > 1:
            for xx in range(0,len(records)-1):
                dt = (records[xx]["time"] - records[xx+1]["time"]).total_seconds();
                dt_sum += dt
                dts.append(dt)
  
            dt_mean = float(dt_sum) / (len(records)-1)
            var_squared = 0
            var_squared_sum =0
            
            for xx in dts:
                var_squared = abs((xx-dt_mean))**2
                var_squared_sum += var_squared
                
            dt_std_dev = math.sqrt(float(var_squared_sum) / (len(records)-1))
            
            
            if abs(dt_mean - ((records[0]["time"] - records[1]["time"]).total_seconds())) > abs(dt_mean - dt_std_dev):
                bored = True

        
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

@csrf.exempt
@app.route('/message-tracker',methods=["GET","POST"])
@login_required
def message_tracker(message_id=""):
    if request.method == 'POST':
        message_id = request.form["message_id"]
        message_times = []
        
        first_message = MessageTimes(message_id)
        first_message.get()
        message_times.append(first_message)
        
        child_messages = first_message.get_child_messages(message_id)
        for c in child_messages:
            m = MessageTimes(c)
            m.get()
            message_times.append(m)
            
        return render_template('message_tracker_detail.html',
                message_id=message_id,
                first_message=first_message,
                message_times=message_times,
                )
        
    else:
        return render_template('message_tracker.html')


@csrf.exempt
@app.route('/detailed-report',methods=["GET","POST"])
@login_required
def detailed_report():
    if request.method == "GET":
        return render_template('detailed_report_start.html')
    else:
        report_start = datetime.now()
        
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        try:
            start_year = int(start_time[:4])
            start_month = int(start_time[4:6])
            start_day = int(start_time[6:])
            end_year = int(end_time[:4])
            end_month = int(end_time[4:6])
            end_day = int(end_time[6:])
        except:
            return render_template("detailed_report_start.html",error="Invalid parameters.")
            
        rows = []
        peak_times = []
        end_day = datetime(end_year,end_month,end_day)
        current_day = datetime(start_year,start_month,start_day)
        one_day = timedelta(days=1)
        two_hours = timedelta(hours=2)
        
        while current_day < end_day:
            print(str(current_day))
            
            responses = mongo.db.sent_responses.find({
                    "message.time_created":{
                        "$gt":current_day,
                        "$lt":current_day + two_hours
                     }
            })
            
            total_responses = responses.count() 
                
            total_time = timedelta()
            for r in responses:
                time = r["time_response_received"] - r["message"]["time_created"]
                total_time += time
            
            if total_responses>0:
                avg = total_time.seconds / total_responses
            else:
                avg = 0
            
            if total_responses > 1000:
                peak_times.append((current_day,total_responses,(total_responses/2)/60, avg))
            
            date_string = datetime.strftime(current_day,"%m/%d %I%p")
            
            rows.append((date_string,int(total_responses),str(total_time),float(avg)))
            current_day = current_day + two_hours
            
        report_end = datetime.now()
        report_time = ((report_end-report_start).seconds) / 60
        #return render_template('detailed_report.html',rows=rows,report_time=report_time)  
        return jsonify({"rows":rows,"peak_times":peak_times,"report_time":report_time})
