from tutors import HintFactoryTutor

from hpitclient.settings import HpitClientSettings
settings = HpitClientSettings.settings()
settings.HPIT_URL_ROOT = 'http://127.0.0.1:8000'

h = HintFactoryTutor("e59139f1-7b30-47a5-b042-8b12689cb1fa","9e97d36835aff7d5f51646723f31fd20",None)
h.start()
