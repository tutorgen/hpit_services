import platform

from common_manager import *

if platform.system() == "Windows":
    from win_manager import *
else:
    from unix_manager import *
    
run_manager()
    
    
