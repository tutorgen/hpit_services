from server.app import ServerApp
db = ServerApp.get_instance().db

class StudentAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.String(255), nullable=False)
    student_id = db.Column(db.String(255), nullable=False)
