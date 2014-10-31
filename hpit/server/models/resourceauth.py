from hpit.server.app import ServerApp
db = ServerApp.get_instance().db

class ResourceAuth(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    entity_id = db.Column(db.String(255), nullable=False)
    resource_id = db.Column(db.String(255),nullable=False)
    is_owner = db.Column(db.Boolean(), nullable=False)
