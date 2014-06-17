import random
from datetime import datetime
from Crypto.Hash import HMAC, SHA512

from server import db, settings

class Plugin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    entity_id = db.Column(db.String(255), nullable=False)
    api_key_salt = db.Column(db.String(255), nullable=False)
    api_key_result = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1400), nullable=False)
    connected = db.Column(db.Boolean, nullable=False, default=False)

    def generate_key(self):
        now = datetime.now()
        random.seed(now)

        #Generate a randomize salt and HMAC it for posterity
        self.api_key_salt = random.randrange(16**30)
        hsh = HMAC.new(bytes(settings.SECRET_KEY.encode('utf-8')))
        hsh.update(bytes(str(self.api_key_salt).encode('utf-8')))

        key = hsh.hexdigest()

        #Generate the resulting hash of key + salt + our_secret
        hsh = SHA512.new(bytes(settings.SECRET_KEY.encode('utf-8')))
        hsh.update(bytes(str(self.api_key_salt).encode('utf-8')))
        hsh.update(bytes(key.encode('utf-8')))

        #Only the resulting hash is stored
        self.api_key_result = hsh.hexdigest()

        #Return the unsaved key
        return key

    def authenticate(self, key):
        hsh = SHA512.new(settings.SECRET_KEY)
        hsh.update(self.api_key_result)
        hsh.update(key)

        if hsh.hexdigest() == self.api_key_result:
            return True

        return False
