
from requests import Request, Session
import requests
from time import *
import hmac
import urllib
import hashlib
import base64
import binascii

from hpitclient import Plugin

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
        if self.logger:
            self.logger.debug("RECV: get_dataset_metadata with message: " + str(payload))
        
        path = "/datasets"
        dataset_id = payload['dataset_id']
        response_to_send = self.datashop_request("GET",str(path)+"/"+str(dataset_id))
 
        self.send_response(payload['message_id'], {
            'reponse_xml':str(response_to_send.text),
            'status_code':str(response_to_send.status_code)
        })
   
    def get_sample_metadata(self,payload):
        if self.logger:
            self.logger.debug("RECV: get_sample_metadata with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = payload['sample_id']
        path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)
        
        response_to_send = self.datashop_request("GET",str(path))
 
        self.send_response(payload['message_id'], {
            'reponse_xml':str(response_to_send.text),
            'status_code':str(response_to_send.status_code)
        })
    
    def get_transactions(self,payload):
        if self.logger:
            self.logger.debug("RECV: get_transactions with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = None
        if "sample_id" in payload:
            sample_id = payload['sample_id']
            path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)+"/transactions"
        else:
            path = "/datasets/"+str(dataset_id) + "/transactions"

        response_to_send = self.datashop_request("GET",str(path))
 
        self.send_response(payload['message_id'], {
            'reponse_xml':str(response_to_send.text),
            'status_code':str(response_to_send.status_code)
        })
    
    def get_student_steps(self,payload):
        if self.logger:
            self.logger.debug("RECV: get_student_steps with message: " + str(payload))
        
        dataset_id = payload['dataset_id']
        sample_id = None
        if "sample_id" in payload:
            sample_id = payload['sample_id']
            path = "/datasets/"+str(dataset_id) + "/samples/" + str(sample_id)+"/steps"
        else:
            path = "/datasets/"+str(dataset_id) + "/steps"
        
        response_to_send = self.datashop_request("GET",str(path))
 
        self.send_response(payload['message_id'], {
            'reponse_xml':str(response_to_send.text),
            'status_code':str(response_to_send.status_code)
        })
    
    def add_custom_field(self,payload):
        if self.logger:
            self.logger.debug("RECV: add_custom_field with message: " + str(payload))
        
        try:
            dataset_id = payload['dataset_id']
            name = payload['name']
            description = payload['description']
            typ = payload['type']
        except KeyError:
            print("Make sure your mayload has a data_id, name, description, and type for the custom field.")
            raise
        
        path = "/datasets/"+str(dataset_id) + "/customfields/add"
        
        response_to_send = self.datashop_request("POST",str(path),data='postData=<?xml version="1.0" encoding="UTF-8"?><pslc_datashop_message><custom_field><name>'+name+'</name><description>'+description+'</description><type>'+typ+'</type><level>transaction</level></custom_field></pslc_datashop_message>')
 
        self.send_response(payload['message_id'], {
            'reponse_xml':str(response_to_send.text),
            'status_code':str(response_to_send.status_code)
        })
        
        
    def datashop_request(self,method,path, headers={},data = ""):
        date_string = strftime("%a, %d %b %Y %H:%M:%S", gmtime()) + " GMT"
        
        encode_string = method+"\n\n\n"+date_string+"\n"+path
        
        #secret_key = "QsNrGW5mJl55nWgqRe33xSsWSvaWPR1J6tRrwXOc"
        #public_key = "8ZCR1X2018MJ1120TW7S"
        
        secret_key = "8woBw0ihGB5z5h7H7w5jPOmoSVfr6BzU6WRGTY33"
        public_key = "ICGU50AVJHGQIIHOWUXZ"
        
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
        if method == "POST":
            headers["content-type"] = "application/x-www-form-urlencoded;charset=utf-8"
        
        s = Session()
        
        #req = Request(method,"https://pslcdatashop.web.cmu.edu/services"+path,headers=headers,data =data)
        
        req = Request(method,"http://pslc-qa.andrew.cmu.edu/datashop/services"+path,headers=headers,data =data)
        
        prepared_req = s.prepare_request(req)
        
        response = s.send(prepared_req)
        
        return response
