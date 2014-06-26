import platform
import sys
from pyenvi.pyenvi import PyEnvi

if "test" in sys.argv:
    pyenvi = PyEnvi({"mode":"TEST"})
    pyenvi.start()
    print(PyEnvi.get_instance())


if platform.system() == "Windows":
    from win_manager import *
else:
    from unix_manager import *
    
run_manager()

try:
    PyEnvi.get_instance().stop()
except Exception:
    pass
