from hpit.server.app import ServerApp
app_instance = ServerApp.get_instance()

from hpit.server.models import Plugin, StudentAuth

class StudentAuthentication(object):
    
    db = app_instance.db
    
    @staticmethod
    def add_student_auth(entity_id,student_id):
        student_auth = StudentAuth()
        student_auth.entity_id = entity_id
        student_auth.student_id = student_id
        StudentAuthentication.db.session.add(student_auth)
        
        plugins = Plugin.query.filter_by(internal=True)
        plugin_ids = [p.entity_id for p in plugins]
        for pid in plugin_ids:
            student_auth = StudentAuth.query.filter_by(entity_id=pid,student_id=student_id).first()
            if not student_auth:
                sa = StudentAuth()
                sa.entity_id = pid
                sa.student_id = student_id
                StudentAuthentication.db.session.add(sa)
        
        StudentAuthentication.db.session.commit()    
        
        return True
    
    @staticmethod
    def student_auth(entity_id,student_id):
        student_auth = StudentAuth.query.filter_by(entity_id=entity_id,student_id=student_id).first()
        if not student_auth:
            return False
        else:
            return True
    
    @staticmethod
    def init_auth():
        #make sure every student is registered with every internal plugin
        plugins = Plugin.query.filter_by(internal=True)
        plugin_ids = [p.entity_id for p in plugins]
        
        student_auths = StudentAuth.query.all()
        student_ids = [s.student_id for s in student_auths]

        for pid in plugin_ids:
            for sid in student_ids:
                auth_item = StudentAuth.query.filter_by(entity_id=pid,student_id=sid).first()
                if not auth_item:
                    sa = StudentAuth()
                    sa.entity_id = pid
                    sa.student_id = sid
                    StudentAuthentication.db.session.add(sa)
         
        StudentAuthentication.db.session.commit()   
         
