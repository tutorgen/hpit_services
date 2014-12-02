import sys
import pprint
from datetime import datetime
from pymongo import MongoClient
import re

def file_len(fname):
    #from http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def get_skills(row):
    skills = {}
    skill_ids = {}
    for k,v in row.items():
        m = re.match(r"^KC \((.*)\)$",k)
        if m:
            kc_model = m.group(1)
            kc_model = kc_model.replace(".","_")
            skills[kc_model] = v
    
    for k,v in skills.items():
        existing_skill = client.hpit.hpit_skills.find_one({
          "skill_name":v,      
        })
        if not existing_skill:
            new_skill = client.hpit.hpit_skills.insert({
                "skill_name":v,
                "skill_model":k,
            })
            skill_id = str(new_skill)
        else:
            skill_id = str(existing_skill["_id"])
    
        skill_ids[v] = skill_id
    
    return skills,skill_ids

def get_levels(row):
    levels = {}
    for k,v in row.items():
        m = re.match(r"^Level \((.*)\)$",k)
        if m:
            level_name = m.group(1)
            level_name = level_name.replace(".","_")
            levels[level_name] = v
            
    return levels

args = sys.argv
if len(args) != 4:
    raise Exception("Not enough / too many command line args.")
    
client = MongoClient()

student_cache = {}
problem_cache = {}
step_cache = {}
transaction_cache = {}

#-------------------------------------------------------------------------------    
#parse problems
#-------------------------------------------------------------------------------
print("parsing problems...")

filein = open(args[1],"r")
filelen = file_len(args[1])
header_line = filein.readline()
headers = header_line.split("\t")

count = 0
while 1:
    line = filein.readline()
    if not line:
        break
    
    print(str(count) + " / " + str(filelen)+ "\r",end="")
    count+=1
    
    values = line.split("\t")
    problem = dict(zip(headers,values))
    
    #insert new student
    if problem["Anon Student Id"] not in student_cache:
        existing_student = client.hpit.hpit_students.find_one({
             "attributes":{
                "other_id":problem["Anon Student Id"]  
             }   
        })
        
        if not existing_student:
            new_student = client.hpit.hpit_students.insert({
            "attributes":{
                "other_id":problem["Anon Student Id"]  
             }})
            student_id = str(new_student)
        else:
            student_id = str(existing_student["_id"])
            
        student_cache[problem["Anon Student Id"]] = student_id
    
    student = student_cache[problem["Anon Student Id"]]
    
    if (problem["Problem Name"],problem["Anon Student Id"]) not in problem_cache:
        existing_problem = client.hpit.hpit_problems.find_one({
                "edit_allowed_id": student,
                "problem_name":problem["Problem Name"],
                "problem_text":problem["Problem Hierarchy"],
            })
        if not existing_problem:
            new_problem = client.hpit.hpit_problems.insert({
                "edit_allowed_id": student,
                "problem_name":problem["Problem Name"],
                "problem_text":problem["Problem Hierarchy"],
                "date_created":datetime.now(),
            })
            problem_id = new_problem
        else:
            problem_id = existing_problem["_id"]
        
        new_problem_worked = client.hpit.hpit_problems_worked.update({
                "student_id": student,
                "problem_id": problem_id
            },
            {
                "student_id": student,
                "problem_id": problem_id,
        },upsert=True)
        
        problem_cache[(problem["Problem Name"],problem["Anon Student Id"])] = problem_id   
    
#-------------------------------------------------------------------------------    
#parse steps
#-------------------------------------------------------------------------------
print("parsing steps...")

filein = open(args[2],"r")
filelen = file_len(args[2])
header_line = filein.readline()
headers = header_line.split("\t")

count = 0
while 1:
    line = filein.readline()
    if not line:
        break
    
    print(str(count) + " / " + str(filelen)+ "\r",end="")
    count+=1
    
    values = line.split("\t")
    step = dict(zip(headers,values))
    
    skill_tuple = get_skills(step)
    
    if (step["Step Name"],step["Anon Student Id"]) not in step_cache:
        problem = problem_cache[(step["Problem Name"],step["Anon Student Id"])]
        student = student_cache[step["Anon Student Id"]]
        
        existing_step = client.hpit.hpit_steps.find_one({
            "problem_id":problem,
            "step_text": step["Step Name"],
            "allowed_edit_id": student,
        })
        if not existing_step:
            new_step = client.hpit.hpit_steps.insert({
                    "problem_id":problem,
                    "step_text": step["Step Name"],
                    "allowed_edit_id": student,
                    "date_created":datetime.now(),
                    "skill_ids": skill_tuple[1],
                    "skill_names": skill_tuple[0],
            })
            step_id = new_step
        else:
            step_id = existing_step["_id"]
        
        step_cache[(step["Step Name"],step["Anon Student Id"])] = step_id
    
#-------------------------------------------------------------------------------    
#parse transactions
#-------------------------------------------------------------------------------
print("parsing transactions...")

filein = open(args[3],"r")
filelen = file_len(args[3])
header_line = filein.readline()
headers = header_line.split("\t")

count = 0
while 1:
    line = filein.readline()
    if not line:
        break
        
    print(str(count) + " / " + str(filelen) + "\r",end="")
    count+=1
    
    values = line.split("\t")
    transaction = dict(zip(headers,values))
    
    skill_tuple = get_skills(transaction)
    levels = get_levels(transaction)
    
    step_id = step_cache[(transaction["Step Name"],transaction["Anon Student Id"])]
    student = student_cache[transaction["Anon Student Id"]]
    
    if (transaction["Transaction Id"],transaction["Anon Student Id"]) not in transaction_cache:
        existing_transaction = client.hpit.hpit_transactions.find_one({
            "transaction_text":transaction["Transaction Id"],
            "step_id":step_id,
            "student_id":transaction["Anon Student Id"],
            "session_id":transaction["Session Id"],
        })
        
        if not existing_transaction:
            new_transaction = client.hpit.hpit_transactions.insert({
                "transaction_text":transaction["Transaction Id"],
                "step_id":step_id,
                "allowed_edit_id":"-1",
                "date_created":datetime.now(),
                "skill_ids": skill_tuple[1],
                "skill_names": skill_tuple[0],
                "student_id":student,
                "session_id": transaction["Session Id"],
                "level_names": levels,
                
            })
            transaction_id = new_transaction
        else:
            transaction_id = existing_transaction["_id"]
            
        transaction_cache[(transaction["Transaction Id"],transaction["Anon Student Id"])] = transaction_id
            
        
        
        
    
    
