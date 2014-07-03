
from requests import Request, Session
import requests
from time import *
import hmac
import urllib
import hashlib
import base64
import binascii

from client import Plugin

class DataShopConnectorPlugin(Plugin):
    
    def __init__(self,entity_id,api_key,logger,args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        
        self.datashop_services_root = "https://pslcdatashop.web.cmu.edu/services"
        
    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            get_dataset_metadata=self.get_dataset_metadata,
            get_sample_metadata=self.get_sample_metadata,
            get_transactions=self.get_transactions,
            get_student_steps=self.get_student_steps,
            add_custom_field=self.add_custom_field)
        
   
    def get_dataset_metadata(self,payload):
        self.logger.debug("RECV: get_dataset_metadata with message: " + str(payload))
        
        path = "/datasets"
        dataset_id = payload['dataset_id']
        response_to_send = self.datashop_request(str(path)+"/"+str(dataset_id))
 
        self.send_response(payload['_message_id'], {
            'reponse_xml':str(response_to_send.text),       
        })
   
    def get_sample_metadata(self,payload):
        self.logger.debug("RECV: get_sample_metadata with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = payload['sample_id']
        path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)
        
        response_to_send = self.datashop_request(str(path))
 
        self.send_response(payload['_message_id'], {
            'reponse_xml':str(response_to_send.text),       
        })
    
    def get_transactions(self,payload):
        self.logger.debug("RECV: get_transactions with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = None
        if "sample_id" in payload:
            sample_id = payload['sample_id']
            path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)+"/transactions"
        else:
            path = "/datasets/"+str(dataset_id) + "/transactions"
        
        response_to_send = self.datashop_request(str(path))
 
        self.send_response(payload['_message_id'], {
            'reponse_xml':str(response_to_send.text),       
        })
    
    def get_student_steps(self,payload):
        self.logger.debug("RECV: get_student_steps with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = None
        if "sample_id" in payload:
            sample_id = payload['sample_id']
            path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)+"/steps"
        else:
            path = "/datasets/"+str(dataset_id) + "/steps"
        
        response_to_send = self.datashop_request(str(path))
 
        self.send_response(payload['_message_id'], {
            'reponse_xml':str(response_to_send.text),       
        })
    
    def add_custom_field(self,payload):
        self.logger.debug("RECV: add_custom_field with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        path = "/datasets/"+str(dataset_id) + "/customfields/add"
        
        response_to_send = self.datashop_request(str(path),{"name":"HPIT Field","description":"A custom field added from HPIT","type":"string","level":"transaction"})
 
        self.send_response(payload['_message_id'], {
            'reponse_xml':str(response_to_send.text),       
        })
        
        
    def datashop_request(self,path, headers={}):
        date_string = strftime("%a, %d %b %Y %H:%M:%S", gmtime()) + " GMT"
        
        encode_string = "GET\n\n\n"+date_string+"\n"+path
        
        secret_key = "QsNrGW5mJl55nWgqRe33xSsWSvaWPR1J6tRrwXOc"
        public_key = "8ZCR1X2018MJ1120TW7S"
        
        dig = hmac.new(bytes(secret_key,"utf-8"), msg=bytes(encode_string,"utf-8"), digestmod=hashlib.sha1).digest()
        keyhash = binascii.b2a_base64(dig)
        keyhash = keyhash.decode("utf-8")
        keyhash = keyhash.rstrip("\n")
        keyhash = keyhash + "\r\n"
        keyhash = urllib.parse.quote_plus(keyhash)
        
        headers['User-Agent'] = 'python-requests/1.2.0'
        headers['date'] = date_string
        headers['authorization'] = "DATASHOP " + public_key +":" + keyhash
        headers['accept'] = "text/xml"
        
        
        s = Session()
        
        req = Request("GET","https://pslcdatashop.web.cmu.edu/services"+path,headers=headers)#,data ="here is the data")
       
        prepared_req = s.prepare_request(req)
        
        response = s.send(prepared_req)
        
        return response
