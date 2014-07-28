import unittest
from unittest.mock import *
import responses

from hpitclient.settings import HpitClientSettings
HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT

from plugins import DataShopConnectorPlugin

class TestDataShopConnectorPlugin(unittest.TestCase):
    
    class DummyResponse(object):
        def __init__(self):
            self.text = "text"
            self.status_code = "200"
    
    def test_constructor(self):
        """
        DataShopConnectorPlugin.__init__() Test plan:
            - make sure logger set
            - make sure datashop_services_root is "https://pslcdatashop.web.cmu.edu/services"
        """
        d = DataShopConnectorPlugin("1234","1234","logger",None)
        d.logger.should.equal("logger")
        d.datashop_services_root.should.equal("https://pslcdatashop.web.cmu.edu/services")
    
    def test_get_dataset_metadata(self):
        """
        DataShopConnectorPlugin.get_dataset_metadata() Test plan:
            - send in a payload with id
            - mock datashop request to return a response class with text and status code
            - ensure called with get, dataset path, and the id
            - mock out send response, make sure called with a message_id and stuff from response
        """
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request = MagicMock(return_value=TestDataShopConnectorPlugin.DummyResponse())
        d.send_response = MagicMock()
        d.get_dataset_metadata({"message_id":4,"dataset_id":5})
        
        d.datashop_request.assert_called_with("GET","/datasets/5")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
    
    def test_get_sample_metadata(self):
        """
        DataShopConnectorPlugin.get_sample_metadata() Test plan:
            - send in a payload with dataset, sample, and message id
            - mock datashop request to return a dummy response
            - ensure called with get and path
            - mouch send response, make sure called with message id and dummy response
        """
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request = MagicMock(return_value=TestDataShopConnectorPlugin.DummyResponse())
        d.send_response = MagicMock()
        d.get_sample_metadata({"message_id":4,"dataset_id":5,"sample_id":6})

        d.datashop_request.assert_called_with("GET","/datasets/5/samples/6")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
        
    
    def test_get_transactions(self):
        """
        DataShopConnectorPlugin.get_transactions() Test plan:
            - send in a dataset id and sample id, or just a dataset id
            - if just dataset id, path should be datasets/id/transactions
            - if sampleid too, then path should  be datasets/id/samples/id/transactions
            - mock datashop request and make sure called with GET and path, return dummy response
            - mock send response, make sure called with message id and dummy response
        """
        
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request = MagicMock(return_value=TestDataShopConnectorPlugin.DummyResponse())
        d.send_response = MagicMock()
        
        d.get_transactions({"message_id":4,"dataset_id":5,"sample_id":6})
        d.datashop_request.assert_called_with("GET","/datasets/5/samples/6/transactions")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
        
        d.datashop_request.reset_mock()
        d.send_response.reset_mock()
        
        d.get_transactions({"message_id":4,"dataset_id":5})
        d.datashop_request.assert_called_with("GET","/datasets/5/transactions")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
        

    def test_get_student_steps(self):
        """
        DataShopConnectorPlugin.get_student_steps() Test plan:
            - send in a dataset id and sample id, or just a dataset id
            - if just dataset id, path should be datasets/id/steps
            - if sampleid too, then path should  be datasets/id/samples/id/steps
            - mock datashop request and make sure called with GET and path, return dummy response
            - mock send response, make sure called with message id and dummy response
        """
        
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request = MagicMock(return_value=TestDataShopConnectorPlugin.DummyResponse())
        d.send_response = MagicMock()
        
        d.get_student_steps({"message_id":4,"dataset_id":5,"sample_id":6})
        d.datashop_request.assert_called_with("GET","/datasets/5/samples/6/steps")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
        
        d.datashop_request.reset_mock()
        d.send_response.reset_mock()
        
        d.get_student_steps({"message_id":4,"dataset_id":5})
        d.datashop_request.assert_called_with("GET","/datasets/5/steps")
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
        
    
    def test_add_custom_field(self):
        """
        DataShopConnectorPlugin.add_custom_field() Test plan:
            - send in dataset id, name, description, typ.  key error raised if one is missing
            - mock datashop_request, return dummy response, make sure called with GET, path, and data attached
            - mock send response, make sure called with emssage id and dummy reponse
        """
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request = MagicMock(return_value=TestDataShopConnectorPlugin.DummyResponse())
        d.send_response = MagicMock()
        d.add_custom_field.when.called_with({"message_id":4,"dataset_id":5}).should.throw(KeyError)
        d.add_custom_field.when.called_with({"message_id":4,"dataset_id":5,"name":"name"}).should.throw(KeyError)
        d.add_custom_field.when.called_with({"message_id":4,"dataset_id":5,"name":"name","description":"description"}).should.throw(KeyError)
        
        d.add_custom_field({"message_id":4,"dataset_id":5,"name":"name","description":"description","type":"typ"})
        
        d.datashop_request.assert_called_with("POST","/datasets/5/customfields/add",data='postData=<?xml version="1.0" encoding="UTF-8"?><pslc_datashop_message><custom_field><name>name</name><description>description</description><type>typ</type><level>transaction</level></custom_field></pslc_datashop_message>')
        d.send_response.assert_called_with(4,{
            'reponse_xml':"text",
            'status_code':"200"
        })
    
    def test_datashop_request(self):
        """
        DataShopConnectorPlugin.datashop_request() Test plan:
            -issue hello world request. make sure status is ok
        """
        d = DataShopConnectorPlugin("1234","1234",None,None)
        d.datashop_request("GET","/helloworld").text.should.equal('<?xml version="1.0" encoding="UTF-8"?>\n<pslc_datashop_message result_code="0" result_message="Success. Hello World!"/>\n')
