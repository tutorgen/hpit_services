from server.app import ServerApp
db = ServerApp.get_instance().db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plugin_id = db.Column(db.Integer, db.ForeignKey('plugin.id'))
    message_name = db.Column(db.String(255), nullable=False)
