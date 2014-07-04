import os
from Crypto.Hash import HMAC, SHA512

from server.app import ServerApp
db = ServerApp.get_instance().db

from server.settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    entity_id = db.Column(db.String(255), nullable=False)
    api_key_salt = db.Column(db.String(255), nullable=False)
    api_key_result = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1400), nullable=False)
    connected = db.Column(db.Boolean, nullable=False, default=False)

    def generate_key(self):
        #Generate a cryptographically secure key with HMAC
        hsh = HMAC.new(bytes(settings.SECRET_KEY.encode('utf-8')))
        hsh.update(os.urandom(128))

        key = hsh.hexdigest()

        #Generate a cryptographically secure random salt
        self.api_key_salt = str(os.urandom(32))

        #Generate the resulting hash of key + salt + our_secret
        hsh = SHA512.new(bytes(settings.SECRET_KEY.encode('utf-8')))
        hsh.update(bytes(self.api_key_salt.encode('utf-8')))
        hsh.update(bytes(key.encode('utf-8')))

        #Only the resulting hash is stored
        self.api_key_result = hsh.hexdigest()

        #Return the unsaved key
        return key

    def authenticate(self, key):
        hsh = SHA512.new(bytes(settings.SECRET_KEY.encode('utf-8')))
        hsh.update(bytes(self.api_key_salt.encode('utf-8')))
        hsh.update(bytes(key.encode('utf-8')))

        if hsh.hexdigest() == self.api_key_result:
            return True

        return False
