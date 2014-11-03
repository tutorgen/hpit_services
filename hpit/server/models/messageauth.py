from hpit.server.app import ServerApp
db = ServerApp.get_instance().db

class MessageAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.String(255), nullable=False)
    message_name = db.Column(db.String(255), nullable=False)
    is_owner = db.Column(db.Boolean(), nullable=False)
