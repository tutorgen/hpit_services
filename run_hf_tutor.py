from tutors import HintFactoryTutor
import argparse
from hpitclient.settings import HpitClientSettings

settings = HpitClientSettings.settings()
settings.HPIT_URL_ROOT = 'http://127.0.0.1:8000'

parser = argparse.ArgumentParser(description='Entity id and secret')
parser.add_argument('entity_id', type=str, help="The entity ID of the entity.")
parser.add_argument('api_key', type=str, help="The api key of the entity.")

arguments = parser.parse_args()

h = HintFactoryTutor(arguments.entity_id,arguments.api_key,None)
h.start()
