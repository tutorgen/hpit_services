"""
This script takes the output from the load testing tutor and creates a report.
"""

import sys

class ThreadStats(object):
    
    def __init__(self,name):
        self.name = name
        self.times = []
        
        self.sumi = None
        self.avg = None
        self.mini = None
        self.maxi = None
        self.total = None
    
    def __str__(self):
        return "{}> Sum: {} Average: {} Min: {} Max: {} Total: {}".format(self.name,self.sumi,self.avg,self.mini,self.maxi,self.total)
    
    def get_metrics(self):
        self.sumi = sum(self.times)
        self.avg = self.sumi / len(self.times)
        self.mini = min(self.times)
        self.maxi = max(self.times)
        self.total = len(self.times)

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
        
for k in sorted(threadstats):
    threadstats[k].get_metrics()
    print(threadstats[k])

