from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter.ttk import Treeview

import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
import json
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
import pytz
import signal

from hpitclient import Tutor

def file_len(fname):
    #from http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def get_skills(row):
    """
    Arguments: a row of transaction, a dictionary of header to column value pairs.
    Returns: skills-  skill models to skill names
    """ 
    skills = {}
    skill_ids = {}
    for k,v in row.items():
        m = re.match(r"^KC \((.*)\)$",k)
        if m:
            kc_model = m.group(1)
            kc_model = kc_model.replace(".","_")
            skills[kc_model] = v
    
    return skills

class ReplayTutor2(Tutor):
    """
    ReplayTutor:  a tutor for testing/backup purposes, that re-sends messages to plugins.
    """
    def __init__(self, entity_id, api_key, logger, run_once=None, args=None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        
        self.student_id_value = None
        self.session_id_value = None
        
        self.root = None
        self.status = None
        self.student_id = None
        self.session_id = None
        self.problem_name = None
        self.step_name = None
        self.transaction_id = None
        self.outcome = None
        self.skillbox = None
        self.button = None
        self.kt_button = None
        self.attr_name = None
        self.attr_value = None
        self.attr_button = None
        self.skill_id = None
        self.kt_button = None
        self.response_box = None
        
        self.json_in = None
        
    def post_connect(self):
        self.send("tutorgen.add_student",{},self.new_student_callback)
    
    def setup_gui(self):
        #main window
        self.root = Tk()
        self.root.wm_title("Transaction Replay Tutor")
        self.root.minsize(400,400)
    
        #menu
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import Datashop File", command=self.import_datashop_file)
        filemenu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        
        #listbox
        w = Label(self.root, text="Transaction")
        w.pack(fill=X)
        
        frame = Frame()
        scrollbar = Scrollbar(frame, orient=VERTICAL)
        
        self.treeview = Treeview(frame,yscrollcommand=scrollbar.set)
        self.treeview["columns"] = ("problem_name","step_text","transaction_text","skill_names","outcome")
        self.treeview.heading("problem_name",text="Problem Name")
        self.treeview.heading("step_text",text="Step Text")
        self.treeview.heading("transaction_text",text="Transaction Text")
        self.treeview.heading("skill_names",text="Skill Names")
        self.treeview.heading("outcome",text="Outcome")
        
        self.treeview.bind('<<TreeviewSelect>>', self.populate_form)
    
        scrollbar.config(command=self.treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.treeview.pack(side=LEFT, fill=BOTH, expand=1)
        
        frame.pack(fill=BOTH)
        
        #spacer frame
        separator = Frame(height=2, bd=1, relief=SUNKEN)
        separator.pack(fill=X, padx=5, pady=5)
        
        #student id
        w = Label(self.root, text="Student ID")
        w.pack(fill=X)
        self.student_id = Entry(self.root,state=DISABLED)
        self.student_id.pack(fill=X)
        
        #ssession id
        w = Label(self.root, text="Session ID")
        w.pack(fill=X)
        self.session_id = Entry(self.root,state=DISABLED)
        self.session_id.pack(fill=X)
        
        bigframe = Frame()
        bigframe.pack(fill=X,padx =5, ipady=5)
        leftframe = Frame(bigframe)
        leftframe.pack(side=LEFT,fill=X,expand=1)
        rightframe= Frame(bigframe)
        rightframe.pack(side=RIGHT,fill=X,expand=1)
        
        #Entry fields
        ##problem name
        w = Label(leftframe, text="Problem Name")
        w.pack(fill=X)
        self.problem_name = Entry(leftframe)
        self.problem_name.pack(fill=X)
        
        ##step name
        w = Label(leftframe, text="Step Name")
        w.pack(fill=X)
        self.step_name = Entry(leftframe)
        self.step_name.pack(fill=X)
        
        ##Transaction ID
        w = Label(leftframe, text="Transaction ID")
        w.pack(fill=X)
        self.transaction_id = Entry(leftframe)
        self.transaction_id.pack(fill=X)
        
        ##Outcome
        w = Label(leftframe, text="Outcome")
        w.pack(fill=X)
        self.outcome = Entry(leftframe)
        self.outcome.pack(fill=X)
        
        ##skill names
        w = Label(rightframe, text="Skill Models and Names")
        w.pack(fill=X)
        self.skillbox = Text(rightframe,height=8)
        self.skillbox.pack()
        
        #Submit button
        self.button = Button(self.root, text="Send", command=self.submit_transaction, state=DISABLED)
        self.button.pack()

        #spacer frame
        separator = Frame(height=2, bd=1, relief=SUNKEN)
        separator.pack(fill=X, padx=5, pady=5)
        
        bigframe = Frame()
        bigframe.pack(fill=X)
        leftframe = Frame(bigframe,bd=1)
        leftframe.pack(side=LEFT,expand=1, padx =5, ipady=5)
        rightframe= Frame(bigframe,bd=1)
        rightframe.pack(side=RIGHT,expand=1, padx =5, ipady=5)
        
        #student attribute
        w = Label(leftframe, text="Student Attribute")
        w.pack(fill=X)
        self.attr_name = Entry(leftframe)
        self.attr_name.pack(fill=X)
        
        w = Label(leftframe, text="Value")
        w.pack(fill=X)
        self.attr_value = Entry(leftframe)
        self.attr_value.pack(fill=X)
        
        self.attr_button = Button(leftframe, text="Set", command=self.set_attribute, state=DISABLED)
        self.attr_button.pack()
        
        b = Button(leftframe, text="Get", command=self.get_attribute)
        b.pack()
        
        b = Button(leftframe, text="Get Student By Attribute",command=self.get_student_by_attribute)
        b.pack()
        
        #b = Button(leftframe, text="Add Problem", command=self.add_problem)
        #b.pack()
        
        #kt_trace
        w = Label(rightframe, text="Skill ID")
        w.pack(fill=X)
        self.skill_id = Entry(rightframe)
        self.skill_id.pack(fill=X)
        
        self.kt_button = Button(rightframe, text="Trace", command=self.kt_trace, state=DISABLED)
        self.kt_button.pack()
        
        b = Button(rightframe, text="Reset", command=self.kt_reset)
        b.pack()
        
        #response box
        w = Label(self.root, text="Responses")
        w.pack(fill=X)
        self.response_box = Text(height=8)
        self.response_box.pack()
        
        #status
        self.status = Label(text="Status: Idle", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)
    
    def main_loop(self):
        
        again = True
        
        
        if not self.callback():
            again = False

        responses = self._poll_responses()

        if not self._dispatch_responses(responses):
            again = False

        if again:
            self.root.after(self.poll_wait, self.main_loop)
        else:
            raise Exception("Error in main loop")
    
    def import_datashop_file(self):
        
        filename = filedialog.askopenfilename()
        
        with open(filename,"r") as filein:
            header_line = filein.readline()
            headers = header_line.split("\t")
        
        filelen = file_len(filename)       
        count =0
        
        with open(filename,"r") as filein:
            filein.readline() #skip header line
            while 1:
                line = filein.readline()
                if not line:
                    break
                
                rt.status.config(text="Status: Importing Datashop file... " + str(count) + " / " + str(filelen))
                rt.status.update_idletasks()
                
                count+=1
                
                values = line.split("\t")
                transaction = dict(zip(headers,values))
                
                skills = get_skills(transaction)
                
                #("problem_name","step_text","transaction_text","skill_names","outcome")
                rt.treeview.insert("","end",text= "Transaction", values=(transaction["Problem Name"],transaction["Step Name"],transaction["Transaction Id"],json.dumps(skills),transaction["Outcome"]))
        
        rt.status.config(text="Status: Idle")
        rt.status.update_idletasks()
        
        print("file " + filename)
    def add_problem(self):
        mid = self.send("tutorgen.add_problem",{
            "problem_name":"some problem",
            "problem_text":"some problem text",
        }, self.transaction_response_callback)
        
        print(str(mid) + str(datetime.now()))
        
    def kt_trace(self):
        correct=False
        if self.outcome.get().lower() == "correct":
            correct = True
            
        mid = self.send("tutorgen.kt_trace",{
            "student_id":self.student_id.get(),
            "correct":correct,
            "skill_id":self.skill_id.get(),
        }, self.transaction_response_callback)
        
        print(str(mid) + str(datetime.now()))
        
    def kt_reset(self):
        mid = self.send("tutorgen.kt_reset",{
            "student_id":self.student_id.get(),
            "skill_id":self.skill_id.get(),
        }, self.transaction_response_callback)
        
        print(str(mid) + str(datetime.now()))
    
    def set_attribute(self):
        mid = self.send("tutorgen.set_attribute",{
            "student_id":self.student_id.get(),
            "attribute_name":self.attr_name.get(),
            "attribute_value":self.attr_value.get(),
        }, self.transaction_response_callback)
        self.attr_name.delete(0,END)
        self.attr_value.delete(0,END)
        
        print(str(mid) + str(datetime.now()))
        
    def get_attribute(self):
        mid = self.send("tutorgen.get_attribute",{
            "student_id":self.student_id.get(),
            "attribute_name":self.attr_name.get(),
        }, self.transaction_response_callback)
        
        print(str(mid) + str(datetime.now()))
        
        print(str(mid) + str(datetime.now()))
    
    def get_student_by_attribute(self):
        mid = self.send("tutorgen.get_or_create_student_by_attribute",{
            "attribute_name":self.attr_name.get(),
            "attribute_value":self.attr_value.get(),
        }, self.transaction_response_callback)
    
    def populate_form(self,evt):
        w = evt.widget
        item = w.selection()[0]
        values = w.item(item)["values"]

        self.problem_name.delete(0,END)
        self.problem_name.insert(INSERT,values[0])
        
        self.step_name.delete(0,END)
        self.step_name.insert(INSERT,values[1])
        
        self.transaction_id.delete(0,END)
        self.transaction_id.insert(INSERT,values[2])
        
        self.skillbox.delete("0.0",END)
        self.json_in = json.loads(values[3]) #save for later
        json_out = json.dumps(self.json_in, sort_keys=True,indent=4, separators=(',', ': '))
        self.skillbox.insert("0.0",json_out)
        
        self.outcome.delete(0,END)
        self.outcome.insert(INSERT,values[4])
       
    def new_student_callback(self,response):
        self.student_id_value = response["student_id"]
        self.session_id_value = response["session_id"]

        self.student_id.config(state=NORMAL)
        self.student_id.insert(INSERT,str(self.student_id_value))

        self.session_id.config(state=NORMAL)
        self.session_id.insert(INSERT,str(self.session_id_value))
        
        self.button.config(state=NORMAL)
        self.attr_button.config(state=NORMAL)
        self.kt_button.config(state=NORMAL)
    
    def transaction_response_callback(self,response):         
        #messagebox.showinfo("info", "Got a response: " + json.dumps(response, sort_keys=True,indent=4, separators=(',', ': ')))
        self.response_box.insert(END,"\n==========================================")
        self.response_box.insert(END,json.dumps(response, sort_keys=True,indent=4, separators=(',', ': ')))
        
    def submit_transaction(self):
        
        skill_ids = {}
        skill_names = {}
        for skill_model, skill_name in self.json_in.items():
            skill_ids[skill_name] = ""
            skill_names[skill_model] = skill_name
        transaction = {
            "problem_name":self.problem_name.get(),
            "step_text":self.step_name.get(),
            "transaction_text":self.transaction_id.get(),
            "session_id":self.session_id.get(),
            'skill_ids': skill_ids,
            'skill_names': skill_names,
            'student_id':self.student_id.get(),
            'outcome': self.outcome.get(),
            }
        print(transaction)
        print(self.send_transaction(transaction, self.transaction_response_callback))
    
    def main_callback(self):
        return True

if __name__ == "__main__":
    #localhost
    entity_id = "ed188aa3-a673-4482-9475-aedd981ff360"
    app_secret = "e992a697f396a2fd99ef9910cb040fa9"
    url_root = "http://localhost:8000"
    
    #production (tres)
    #entity_id = "e7e43470-5031-496c-9972-cbb809455333"
    #app_secret = "1aadb263acec65c24b683976643516ce"
    #url_root = "http://www.hpit-project.org"
    
    #production (prod)
    #entity_id = "35f8fdda-7f4e-4b48-86ab-eda038186183"
    #app_secret = "d5f1723260ec88293f4fc79f0f7e4572"
    #url_root = "http://production.hpit-project.org"
    
    logging.basicConfig(
            filename="log/datashop_replay.log",
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')
    
    
    logger = logging.getLogger(__name__)
    
    logger.debug("start")
    
    rt = ReplayTutor2(entity_id, app_secret, logger)
    signal.signal(signal.SIGTERM, rt.disconnect)
    rt.set_hpit_root_url(url_root)
    
    rt.setup_gui()

    #main loops
    rt.connect()
    try:
        rt.main_loop()
        rt.root.mainloop()
    except (KeyboardInterrupt, Exception) as e:
        print(str(e))
    rt.disconnect()
