from hpit.server.app import ServerApp
db = ServerApp.get_instance().db

from flask.ext.user import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    administrator = db.Column(db.Boolean(),nullable=False, default = False)
    
    company = db.Column(db.String(255), nullable=False)
    
    
    #email = db.Column(db.String(255), nullable=False, unique=True)
    #confirmed_at = db.Column(db.DateTime())
    #reset_password_token = db.Column(db.String(100), nullable=False, default='')

    #Relationships
    tutors = db.relationship('Tutor', backref='user')
    plugins = db.relationship('Plugin', backref='user')
