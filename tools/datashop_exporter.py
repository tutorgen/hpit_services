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

if len(sys.argv) < 3:
    print ("usage:  python datashop_exporter.py [tutor_id] [output_file]")
else:
    tutor_id = sys.argv[1]
    output_filename = sys.argv[2]
    
client = MongoClient()
fileout = open(output_filename,"w")

transactions = client.hpit.hpit_transactions.find({"edit_allowed_id":str(tutor_id)})

#collect headers
kcs = []
levels = []
for transaction in transactions:
    for k,v in transaction["skill_names"].items():
        kcs.append(k)
    kcs = list(set(kcs))
    for k,v in transaction["level_names"].items():
        levels.append(k)
    levels = list(set(levels))

headers = ["Anon Student Id","Session Id","Time", "Problem Name", "Step Name", "Outcome", "Selection", "Action", "Input"]
headers = headers + ["KC (" +kc + ")" for kc in kcs]
headers = headers + ["Level ("+level+")" for level in levels]
fileout.write("\t".join(headers) + "\n")

#add transactions
transactions.rewind()
for transaction in transactions:
    step = client.hpit.hpit_steps.find_one({"_id":transaction["step_id"]})
    problem = client.hpit.hpit_problems.find_one({"_id":step["problem_id"]})
    line = []
    line = line + [
        transaction["student_id"],
        transaction["session_id"],
        transaction["date_created"].strftime("%Y-%m-%d %H:%M:%S"),
        problem["problem_name"],
        step["step_text"],
        transaction["outcome"],
        transaction["selection"],
        transaction["action"],
        transaction["input"],
    ]
    for kc in kcs:
        try:
            line.append(transaction["skill_names"][kc])
        except KeyError:
            line.append("")
            
    for level in levels:
        try:
            line.append(transaction["level_names"][level])
        except KeyError:
            line.append("")
    
    fileout.write("\t".join(line)+ "\n") 

fileout.close()
