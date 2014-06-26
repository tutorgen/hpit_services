"""
This script is used to start the Flask server on Windows.  In Unix, gunicorn 
is used to start the server, which is coded using relative imports.  This is a 
workaround so the relative imports are preserved in Windows.
"""

from server import app
from server.settings import settings

app.run(port = int(settings.HPIT_BIND_PORT))
