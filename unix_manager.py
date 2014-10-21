import argparse
import json
import subprocess
import os
import time
import signal
import shutil
import sys

from base_manager import BaseManager

class UnixManager(BaseManager):

    def spin_up_all(self, entity_type, configuration):
        """
        Start all entities of a given type, as specified in configuration
        """
        
        entity_collection = self.get_entity_collection(entity_type, configuration)

        for item in entity_collection:
            if not item['active']:
                item['active'] = True
                entity_subtype = item['type']
                entity_id = item['entity_id']
                api_key = item['api_key']

                name = 'Unknown'
                if 'name' in item:
                    name = item['name']
                
                print("Starting entity: " + name + " ID#: " + entity_id)
                pidfile = self.get_entity_pid_file(entity_type, entity_id)
                
                subp_args = [sys.executable, "entity_daemon.py", "--daemon", "--pid", pidfile]

                if 'args' in item:
                    entity_args = shlex.quote(json.dumps(item['args']))
                    subp_args.append("--args")
                    subp_args.append(entity_args)
                    
                if 'once' in item:
                    subp_args.append("--once")
                    
                subp_args.extend([entity_id, api_key, entity_type, entity_subtype])
                
                if entity_type != 'tutor' and entity_type !='plugin':
                    raise Exception("Error: unknown entity type in spin_up_all")
                
                with open("log/output_"+entity_type+"_"+entity_subtype+".txt","w") as f:
                    subprocess.call(subp_args, stdout = f, stderr = f)

    def wind_down_collection(self, entity_type, entity_collection):
        """
        Shut down all entities of a given type from a collection
        """
        
        for item in entity_collection:
            if item['active']:
                item['active'] = False
                entity_id = item['entity_id']
                print("Stopping entity: " + entity_id)
                pidfile = self.get_entity_pid_file(entity_type, entity_id)

                try:
                    with open(pidfile) as f:
                        pid = f.read()
                        os.kill(int(pid), signal.SIGTERM)

                    os.remove(pidfile)
                except FileNotFoundError:
                    print("Error: Could not find PIDfile for entity: " + entity_id)


    def start(self, arguments, configuration):
        """
        Start the hpit server, tutors, and plugins as specified in configuration
        """
        
        if not os.path.exists('tmp'):
            os.makedirs('tmp')

        if not os.path.exists('log'):
            os.makedirs('log')

        if self.server_is_running():
            print("The HPIT Server is already running.")
        else:
            print("Starting the HPIT Hub Server for Unix...")
            with open("tmp/output_server.txt","w") as f:
                subprocess.call(['uwsgi', 
                    '--ini', os.path.join(self.settings.PROJECT_DIR, 'uwsgi_config.ini')],
                    stdout = f, stderr = f)

            for i in range(0, 10):
                print("Waiting " + str(10 - i) + " seconds for the server to boot.\r", end='')
                time.sleep(1)
            print("")

            print("Starting plugins...")
            self.spin_up_all('plugin', configuration)

            for i in range(0, 10):
                print("Waiting " + str(10 - i) + " seconds for the plugins to boot.\r", end='')
                time.sleep(1)
            print("")
            
            print("Starting tutors...")
            self.spin_up_all('tutor', configuration)
        print("DONE!")


    def stop(self, arguments, configuration):
        """
        Stop the hpit server, plugins, and tutors.
        """
        
        if self.server_is_running():
            print("Stopping plugins...")
            self.wind_down_all('plugin', configuration)
            print("Stopping tutors...")
            self.wind_down_all('tutor', configuration)

            print("Stopping the HPIT Hub Server...")
            subprocess.call(['uwsgi', '--stop', '/home/hpitserver/hpitserver.pid'])

            #Cleanup the tmp directory
            shutil.rmtree('tmp')
        else:
            print("The HPIT Server is not running.")
        print("DONE!")
