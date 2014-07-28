import os
import nose

from httpretty.core import fakesock

class Command:
    description = "Unit Test the code."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration
        
        class MySocket(fakesock.socket):
            def real_sendall(self, data, *args, **kw):
                super(MySocket, self).real_sendall(data, *args, **kw)
                # Restore non-zero timeout
                self.truesock.settimeout(self.timeout)

        fakesock.socket = MySocket
        
        nose.main(argv=['-w', os.path.join(os.getcwd(), 'tests'), '--verbose'])
