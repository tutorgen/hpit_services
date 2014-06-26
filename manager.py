import platform
import sys

if platform.system() == "Windows":
    from win_manager import WindowsManager
    manager = WindowsManager()
    manager.run_manager()
else:
    import pdb; pdb.set_trace()
    from unix_manager import UnixManager
    manager = UnixManager()
    manager.run_manager()
