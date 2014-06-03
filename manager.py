import platform
if platform.system() == "Windows":
    from win_manager import *
else:
    from unix_manager import *
    
run_manager()

