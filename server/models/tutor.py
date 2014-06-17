from server import db

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    entity_id = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1400), nullable=False)
    connected = db.Column(db.Boolean, nullable=False, default=False)
