from client import Tutor

class StudentActivityLoggingTutor(Tutor):
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id=entity_id, api_key=api_key, callback=self.work)
        self.run_once = run_once
        self.logger = logger

    def work(self):
        activity = {"subject":"I", "verb":"made", "object":"it"}
        self.send(event_name="activity_logging", payload=activity)
        



