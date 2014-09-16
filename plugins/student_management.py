from hpitclient import Plugin

from pymongo import MongoClient
from bson.objectid import ObjectId

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class StudentManagementPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo.hpit.hpit_students
        

    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            add_student=self.add_student_callback,
            get_student=self.get_student_callback,
            set_attribute=self.set_attribute_callback,
            get_attribute=self.get_attribute_callback)

    #Student Management Plugin
    def add_student_callback(self, message):
        if self.logger:
            self.logger.debug("ADD_STUDENT")
            self.logger.debug(message)
        
        try:
            attributes = message["attributes"]
        except KeyError:
            attributes = {}
            
        student_id = self.db.insert({"attributes":attributes})
        self.send_response(message["message_id"],{"student_id":str(student_id),"attributes":attributes})
        
    def get_student_callback(self, message):
        if self.logger:
            self.logger.debug("GET_STUDENT")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
        except:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id' to get a student"})
            return
        
        return_student = self.db.find_one({"_id":ObjectId(student_id)})
        if not return_student:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
        else:
            self.send_response(message["message_id"],{"student_id":str(return_student["_id"]),"attributes":return_student["attributes"]})
            
    def set_attribute_callback(self, message):
        if self.logger:
            self.logger.debug("SET_ATTRIBUTE")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
            attribute_name = message["attribute_name"]
            attribute_value = message["attribute_value"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
            return
            
        update = self.db.update({'_id':ObjectId(str(student_id))},{'$set':{'attributes.'+str(attribute_name): str(attribute_value)}},upsert=False, multi=False)
        if not update["updatedExisting"]:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
        else:
            record = self.db.find_one({"_id":ObjectId(str(student_id))})
            self.send_response(message["message_id"],{"student_id":str(record["_id"]),"attributes":record["attributes"]})
               
    def get_attribute_callback(self, message):
        if self.logger:
            self.logger.debug("GET_ATTRIBUTE")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
            attribute_name = message["attribute_name"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id' and 'attribute_name'"})
            return 
            
        student = self.db.find_one({'_id':ObjectId(str(student_id))})
        if not student:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
            return
        else:
            try:
                attr = student["attributes"][attribute_name]
            except KeyError:
                attr = ""
            self.send_response(message["message_id"],{"student_id":str(student["_id"]),attribute_name:attr})
        
        
