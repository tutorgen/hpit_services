class DebugServerSettings:
    HPIT_VERSION = '(HPIT) Hyper Personalized Intelligent Tutor(version 0.3) - Codename Bahamut'
    DEBUG = False

    HPIT_PID_FILE = 'tmp/hpit_server.pid'
    HPIT_BIND_IP = "0.0.0.0"
    HPIT_BIND_PORT = "8000"
    HPIT_BIND_ADDRESS = HPIT_BIND_IP+":"+HPIT_BIND_PORT
    PROJECT_DIR = '/Users/raymond/Projects/TutorGen/hpit'
    VENV_DIRNAME = 'env'
    
    MONGO_DBNAME = 'hpit_development'
    SECRET_KEY = 'j#n%$*1+w_op#v4sqc$z2ey+p=9z0#$8ahbs=!8tv3oq$vzc9+'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/hpit_development.sqlite'
    CSRF_ENABLED = True

    #Mail Configuration
    MAIL_DEBUG = True
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 465
    MAIL_USE_SSL  = True                            # Some servers use MAIL_USE_TLS=True instead
    MAIL_USERNAME = 'hpit@tutorgen.com'
    MAIL_PASSWORD = 'abcd1234'
    MAIL_DEFAULT_SENDER = '"HPIT Production" <hpit@tutorgen.com>'

    #Security
    USER_PASSWORD_HASH = 'bcrypt_sha256'

    # Configure Flask-User
    USER_ENABLE_EMAIL            = False
    USER_ENABLE_USERNAME         = True
    USER_ENABLE_CONFIRM_EMAIL    = False
    USER_ENABLE_CHANGE_USERNAME  = False
    USER_ENABLE_CHANGE_PASSWORD  = True
    USER_ENABLE_FORGOT_PASSWORD  = False
    USER_ENABLE_RETYPE_PASSWORD  = True
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/register.html'
    
class TestServerSettings:
    HPIT_VERSION = '(HPIT) Hyper Personalized Intelligent Tutor(version 0.2) - Codename Asura'
    DEBUG = False

    HPIT_PID_FILE = 'tmp/hpit_server.pid'
    HPIT_BIND_IP = "0.0.0.0"
    HPIT_BIND_PORT = "8000"
    HPIT_BIND_ADDRESS = HPIT_BIND_IP+":"+HPIT_BIND_PORT
    PROJECT_DIR = '/Users/raymond/Projects/TutorGen/hpit'
    VENV_DIRNAME = 'env'
    
    MONGO_DBNAME = 'hpit_unit_test_db'
    SECRET_KEY = 'j#n%$*1+w_op#v4sqc$z2ey+p=9z0#$8ahbs=!8tv3oq$vzc9+'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/hpit_unit_test_db.sqlite'
    CSRF_ENABLED = True

    #Mail Configuration
    MAIL_DEBUG = True
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 465
    MAIL_USE_SSL  = True                            # Some servers use MAIL_USE_TLS=True instead
    MAIL_USERNAME = 'hpit@tutorgen.com'
    MAIL_PASSWORD = 'abcd1234'
    MAIL_DEFAULT_SENDER = '"HPIT Production" <hpit@tutorgen.com>'

    # Configure Flask-User
    USER_ENABLE_EMAIL            = False
    USER_ENABLE_USERNAME         = True
    USER_ENABLE_CONFIRM_EMAIL    = False
    USER_ENABLE_CHANGE_USERNAME  = False
    USER_ENABLE_CHANGE_PASSWORD  = True
    USER_ENABLE_FORGOT_PASSWORD  = False
    USER_ENABLE_RETYPE_PASSWORD  = True
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/register.html'

class ProductionServerSettings:
    HPIT_VERSION = '(HPIT) Hyper Personalized Intelligent Tutor(version 0.3) - Codename Bahamut'
    DEBUG = False

    HPIT_PID_FILE = 'tmp/hpit_server.pid'
    HPIT_BIND_IP = "0.0.0.0"
    HPIT_BIND_PORT = "8000"
    HPIT_BIND_ADDRESS = HPIT_BIND_IP+":"+HPIT_BIND_PORT
    PROJECT_DIR = '/Users/raymond/Projects/TutorGen/hpit'
    VENV_DIRNAME = 'env'
    
    MONGO_DBNAME = 'hpit_development'
    SECRET_KEY = 'j#n%$*1+w_op#v4sqc$z2ey+p=9z0#$8ahbs=!8tv3oq$vzc9+'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/hpit_development.sqlite'
    CSRF_ENABLED = True

    #Mail Configuration
    MAIL_DEBUG = True
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 465
    MAIL_USE_SSL  = True                            # Some servers use MAIL_USE_TLS=True instead
    MAIL_USERNAME = 'hpit@tutorgen.com'
    MAIL_PASSWORD = 'abcd1234'
    MAIL_DEFAULT_SENDER = '"HPIT Production" <hpit@tutorgen.com>'

    #Security
    USER_PASSWORD_HASH = 'bcrypt_sha256'

    # Configure Flask-User
    USER_ENABLE_EMAIL            = False
    USER_ENABLE_USERNAME         = True
    USER_ENABLE_CONFIRM_EMAIL    = False
    USER_ENABLE_CHANGE_USERNAME  = False
    USER_ENABLE_CHANGE_PASSWORD  = True
    USER_ENABLE_FORGOT_PASSWORD  = False
    USER_ENABLE_RETYPE_PASSWORD  = True
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/register.html'


class ServerSettingsManager:
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            raise Exception("Instance never initialized")

        return cls.instance

    @classmethod
    def init_instance(cls, environment):
        if not cls.instance:
            cls.instance = ServerSettingsManager(environment)

        return cls.instance

    def __init__(self, environment):
        if environment == 'test':
            self.settings = TestServerSettings
        elif environment == 'production':
            self.settings = ProductionServerSettings
        else:
            self.settings = DebugServerSettings