from client import Tutor
import logging
import os
import time

class DataShopConnectorTutor(Tutor):
    
    def __init__(self,entity_id,api_key,logger,run_once = None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        
        if args: 
            self.args = json.loads(args[1:-1])
        else:
            self.args = None
        
        
    def main_callback(self):         
        print("Main Menu")
        print("0. Quit")
        print("1. Get dataset metadata")
        print("2. Get sample metadata")
        print("3. Get transactions")
        print("4. Get student steps")
        print("5. Add custom field")
        try:
            choice = int(input("==> "))
        except ValueError:
            choice = -1
        
        if choice == 0:
            return False
        elif choice == 1:
            choice = int(input("Dataset id? "))
            self.send("get_dataset_metadata",{"dataset_id":choice},self.print_response_callback)
            time.sleep(2)
        elif choice == 2:
            did = int(input("Dataset id? "))
            sid = int(input("Sample id? "))
            self.send("get_sample_metadata",{"dataset_id":did,"sample_id":sid},self.print_response_callback)
            time.sleep(2)
        elif choice == 3:
            did = int(input("Dataset id? "))
            sid = int(input("Sample id?  (optional, -1 for none)"))
            if sid != -1:
                self.send("get_transactions",{"dataset_id":did,"sample_id":sid},self.print_response_callback)
            else:
                self.send("get_transactions",{"dataset_id":did},self.print_response_callback)
            time.sleep(2)
        elif choice == 4:
            did = int(input("Dataset id? "))
            sid = int(input("Sample id?  (optional, -1 for none)"))
            if sid != -1:
                self.send("get_student_steps",{"dataset_id":did,"sample_id":sid},self.print_response_callback)
            else:
                self.send("get_student_steps",{"dataset_id":did},self.print_response_callback)
            time.sleep(2)
        elif choice == 5:
            did = int(input("Dataset id? "))
            self.send("add_custom_field",{"dataset_id":did},self.print_response_callback)
            time.sleep(2) 
           
        
        print("=====")
        print("")
        
        return True
            
    
    def print_response_callback(self,response):
        print("Response from HIPT: " + str(response))
    
    def run(self):
        self.connect()
        self.start()
        self.disconnect()
        
if __name__ == "__main__":
    logger_path = os.path.join(os.getcwd(), 'log/tutor_71f476d0-55c0-4173-84c2-811edb350d02.log')
    logging.basicConfig(
            filename=logger_path,
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)
    d = DataShopConnectorTutor("71f476d0-55c0-4173-84c2-811edb350d02","479490e3488367963dd96cd9513afe4c",logger,None,None)
    d.run()
