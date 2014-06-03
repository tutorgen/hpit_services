"""
This script is used to start the Flask server on Windows.  In Unix, gunicorn 
is used to start the server, which is coded using relative imports.  This is a 
workaround so the relative imports are preserved in Windows.
"""

import server
from server.settings import HPIT_BIND_PORT

server.app.run(port = int(HPIT_BIND_PORT))
