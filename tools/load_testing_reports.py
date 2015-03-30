import sys

class ThreadStats(object):
    
    def __init__(self,name):
        self.name = name
        self.times = []
        
        self.total = None
        self.avg = None
        self.mini = None
        self.maxi = None
    
    def __str__(self):
        return "{}> Total: {} Average: {} Min: {} Max: {}".format(self.name,self.total,self.avg,self.mini,self.maxi)
    
    def get_metrics(self):
        self.total = sum(self.times)
        self.avg = self.total / len(self.times)
        self.mini = min(self.times)
        self.maxi = max(self.times)

if len(sys.argv) != 2:
    print("Usage: load_testing_reports.py <filename>")
    sys.exit(0)
    

fname = sys.argv[1]
try:
    filein = open(fname,"r")
except FileNotFoundError:
    print("Error: file not found.")
    sys.exit(0)

threadstats = {"All":ThreadStats("All")}
for line in filein:
    words = line.split()
    
    if "RECV" not in words[6]:
        continue
        
    else:
        thread = words[4]
        if thread not in threadstats:
            threadstats[thread] = ThreadStats(thread)
        
        time = words[-2].split(":")
        seconds = float(time[-1])

        threadstats[thread].times.append(float(seconds))
        threadstats["All"].times.append(float(seconds))
        
for k,v in threadstats.items():
    v.get_metrics()
    print(v)

