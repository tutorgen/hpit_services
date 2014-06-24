from client import Tutor
from time import sleep
class StudentActivityLoggingTutor(Tutor):
    def __init__(self, name, logger, run_once=None, args = None):
        super().__init__(name=name, callback=None)
        self.run_once = run_once
        self.logger = logger
        #self.args = json.loads(args[1:-1])

    def work(self):
        log = {"subject":"I", "verb":"made", "object":"it"}
        while True:
            self.send(event_name="activity_logging", payload=log)
            sleep(5)
            #get responses
            #import pdb; pdb.set_trace()
            response = self._poll_responses()
        
    def run(self):
        self.connect()
        #self.start()
        self.work()
        #import pdb; pdb.set_trace()
        self.disconnect()

if __name__ == '__main__':
    tutor = StudentActivityLoggingTutor(name="student_activity_logging")
    tutor.run()



