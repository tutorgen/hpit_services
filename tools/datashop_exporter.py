import sys
from pymongo import MongoClient

"""
Required columns:

Anon Student Id         <=55 Characters
Session Id              <=255 Characters
Time                    yyyy-MM-dd HH:mm:ss
Level(level_name)       <=100 Characters
Problem Name            <=255
Step Name               <=255
KC(kc_model)            <=65,535
"""

client = MongoClient()

problem_names = []
problems = client.hpit.hpit_problems.find({})
for p in problems:
    problem_names.append(p["problem_name"])
    
count =0
num_problems = len(problem_names)
for name in problem_names:
    print(str(count) + " / " + str(num_problems) + "\r",end="")
    count += 1
    problems = client.hpit.hpit_problems.find({"problem_name":name})
    for problem in problems:
        fileout = open(str(sys.argv[1]) + "/" + problem["problem_name"] + str(problem["_id"]) + ".dat","w")
        #collect kcs, levels
        kcs = []
        levels = []
        collected = False
        steps = client.hpit.hpit_steps.find({"problem_id":problem["_id"]})
        for step in steps:
            transactions = client.hpit.hpit_transactions.find({"step_id":step["_id"]})
            for transaction in transactions:
                if not collected:
                    for k,v in transaction["skill_names"].items():
                        kcs.append(k)
                    kcs = list(set(kcs))
                    for k,v in transaction["level_names"].items():
                        levels.append(k)
                    levels = list(set(levels))
                    
                    #headers
                    headers = ["Anon Student Id","Session Id","Time", "Problem Name", "Step Name"]
                    headers = headers + ["KC (" +kc + ")" for kc in kcs]
                    headers = headers + ["Level ("+level+")" for level in levels]
                    fileout.write("\t".join(headers) + "\n")
                    
                    collected = True
                    transactions.rewind()
                    continue;
                
                line = []
                line = line + [
                    transaction["student_id"],
                    transaction["session_id"],
                    transaction["date_created"].strftime("%Y-%m-%d %H:%M:%S"),
                    problem["problem_name"],
                    step["step_text"],
                ]
                line = line + [ transaction["skill_names"][kc] for kc in kcs ]
                line = line + [ transaction["level_names"][level] for level in levels ]
                
                fileout.write("\t".join(line)+ "\n") 
