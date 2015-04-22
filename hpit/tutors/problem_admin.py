from hpitclient import Tutor
import logging
import signal

import traceback, sys

class CLIObject(object):
    def __init__(self):
        self.spacer = "\n"
        self.prompt = ">"
        self.back_input = 'q'
        
    def print_error(self,msg):
        print("*** " + msg + " ***")
        
    def print_status(self,msg):
        print("!! " + msg)

class CLIInput(CLIObject):
    def __init__(self,question):
        super().__init__()
        self.question = question
        self.answer = None
        
    def display(self):
        self.answer = input(self.prompt + " " + self.question) 
        return False

class CLIBoolean(CLIInput):
    
    def display(self):
        answer = input(self.prompt + " " + self.question + " [y/n]")
        if answer.lower() == "y" or answer.lower()== "yes":
            self.answer = True
            return False
        elif answer.lower() == "n" or answer.lower()=="no":
            self.answer = False
            return False
        else:
            self.print_error("Invalid input.")
            return True
            
class CLIForm(CLIObject):
    """TODO validator function
    """
    def __init__(self, title, questions):
        super().__init__()
        
        self.title = title
        self.questions = questions
        
        self.current_question = 0
        self.answers = {}
    
    def _show_review(self):
        for question in self.questions:
            if question[1] in self.answers:
                print("\t" + question[0] + " : " + self.answers[question[1]])
            else:
                print("\t" + question[0] + " : ")
    
    def display(self):
        print(self.spacer,end="",flush=True)
        print(self.title)
        print("(n)ext, (b)ack, (r)eview, " + self.back_input + " to quit.")
        if self.questions[self.current_question][1] in self.answers:
            current_answer = "[" + self.answers[self.questions[self.current_question][1]] + "]"
        else:
            current_answer = "[none]"
        print(str(self.current_question + 1) + "/" + str(len(self.questions)) + " " + self.questions[self.current_question][0] + " " + current_answer)
            
        answer = input(self.prompt)
        if answer == self.back_input:
            self._show_review()
            return False
        elif answer == "n":
            if self.current_question < len(self.questions)-1:
                self.current_question +=1
            return True
        elif answer == "b":
            if self.current_question > 0:
                self.current_question -=1
            return True
        elif answer == "r":
            self._show_review()
            return True
        else:
            self.answers[self.questions[self.current_question][1]] = answer
            self.current_question +=1
            if self.current_question >= len(self.questions):
                self.current_question = 0
            return True
    
    def is_complete(self,elements=None):
        try:
            if elements:
                return all([self.answers[k] for k in elements])
            else:
                return all([self.ansers[k] for k in self.answers]) 
        except KeyError:
            return False
            
class CLIMenu(CLIObject):
    def __init__(self, title, options):
        super().__init__()
        
        self.title = title
        self.options = options
        
    def display(self):
        print(self.spacer,end="",flush=True)
        print(self.title)
        
        count = 0
        for item in self.options:
            print("\t" + str(count) +  " : " + item[0])
            count +=1
            
        print("Press '"+str(self.back_input)+"' to go back.")
        
        selection = input(self.prompt)
        
        #try:
        if str(selection) == str(self.back_input):
            return False
        elif int(selection) < 0 or int(selection) >= len(self.options):
            self.print_error("Invalid input.")
            return True
        else:
            self.options[int(selection)][1]()
            return True
        #except (TypeError, ValueError) as e:
            #self.print_error("Invalid input. ")
            #return True
            
class CLITable(CLIObject):
    def __init__(self,title,rows,headers=[],separator="\t",rows_per_page=10):
        super().__init__()
        
        self.title = title
        self.rows = rows
        self.headers = headers
        self.separator = separator
        self.rows_per_page=rows_per_page
        
        self.page=0
        
    def _show_table(self):
        print(self.spacer,end="",flush=True)
        print(self.title + ": " + str(self.page+1) + "/" + str((len(self.rows) // self.rows_per_page)+1 ))
        if self.headers:    
            print(self.separator.join(self.headers))
        for xx in range(self.page*self.rows_per_page,self.page*self.rows_per_page+self.rows_per_page):
            if xx < len(self.rows):
                print_list = [str(xx)] + self.rows[xx]
                print(self.separator.join(print_list))
    
    def _get_input(self):
        print("(n)ext, (b)ack, " + self.back_input + " to quit.")
        selection = input(self.prompt)
        
        if selection == self.back_input:
            return False
        elif selection == "n":
            if self.page < len(self.rows) // self.rows_per_page:
                self.page+=1
            return True
        elif selection == "b":
            if self.page > 0:
                self.page -=1
            return True
        else:
            self.print_error("Invalid input.")
            return True
            
    def display(self):
        self._show_table()
        return self._get_input()
        
class CLISelectTable(CLITable): 
    """TODO: select ranges 
    """
    def __init__(self,title,rows,headers=[],separator="\t",rows_per_page=10):
        super().__init__(title,rows,headers=headers,separator=separator,rows_per_page=rows_per_page)
        
        self.last_selected = None
    
    def _get_input(self):
        print("(n)ext, (b)ack, "+self.back_input+ " to quit, or selection")
        selection = input(self.prompt)
        
        if selection == self.back_input:
            return False
        elif selection == "n":
            if self.page < len(self.rows) // self.rows_per_page:
                self.page+=1
            return True
        elif selection == "b":
            if self.page > 0:
                self.page -=1
            return True
        elif int(selection) >=0 and int(selection)<len(self.rows):
            self.last_selected = self.rows[int(selection)]
            return False
        else:
            self.print_error("Invalid input.")
            return True
        
        
            
#########################################################################
##
#########################################################################
        
        
        


class ProblemAdmin(Tutor,CLIObject):
    def __init__(self, entity_id, api_key, logger, run_once=None, args=None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        
        self.run_once = run_once
        self.logger = logger
        
        self.main_menu = CLIMenu("Main Menu",[
                ("View Problems",self.view_problems),
                ("Add Problem",self.add_problem),
                ("Delete Problem",self.delete_problem),
                ("Add Step",self.add_step),
                ("Delete Step",self.delete_step),
                ("Batch Load Problems",self.batch_load)
        ])
        
    def _get_problems(self):
        self.print_status("Fetching problems...")
        response = self.send_blocking("tutorgen.list_problems",{"my_problems":True})
        
        problems = []
        if "error" not in response:
            for p in response["problems"]:
                problems.append([
                  p["problem_name"],
                  p["problem_text"],
                  p["date_created"],
                  p["problem_id"],
                ])
            return problems,None
        else:
            return problems,response["error"]    
    
    def _get_steps(self, problem_id):
        self.print_status("Fetching steps...")
        response = self.send_blocking("tutorgen.get_problem_steps",{"problem_id":problem_id})
        
        steps = []
        if "error" not in response:
            for s in response["steps"]:
                steps.append([
                    s["step_id"],
                    s["step_text"],
                    str(s["date_created"]),
                    str(s["skill_ids"])
                ])
            return steps,None
        else:
            return steps,response["error"]
                
                
        
    
    def view_problems(self):
        problems,error = self._get_problems()

        if not error:
            problem_table = CLISelectTable("View Problems",problems)
            
            while 1:
                while(problem_table.display()):
                    pass
                
                if problem_table.last_selected:
                    steps,error = self._get_steps(problem_table.last_selected[-1])
                    if not error:
                        step_table = CLITable("View Steps",steps)
                        while(step_table.display()):
                            pass
                    else:
                        self.print_error(error)
                        
                    problem_table.last_selected = None
                    continue
                else:
                    break 
        else:
            self.print_error(error)
   
    def add_problem(self):
        form = CLIForm("Add a problem:",[
                ("Problem Name:","problem_name"),
                ("Problem Text:","problem_text"),
        ])
        while(form.display()):
            pass
        
        if form.is_complete():
            response = self.send_blocking("tutorgen.add_problem",{"problem_name":form.answers["problem_name"],"problem_text":form.answers["problem_text"]})
            if "error" in response:
                self.print_error(response["error"])
            else:
                self.print_status("Added problem.")
        else:
            self.print_error("Incomplete form.")
         
    def delete_problem(self):
        problems,error = self._get_problems()
        if not error:
            problem_table = CLISelectTable("Delete Problem",problems)
            while(problem_table.display()):
                pass
            selection = problem_table.last_selected
            if selection:
                response = self.send_blocking("tutorgen.remove_problem",{"problem_id":selection[3]})
                if "error" not in response:
                    self.print_status("Removed problem.")
                else:
                    self.print_error(response["error"])
        else:
            self.print_error(error)
    
    def add_step(self):
        problems,error = self._get_problems()
        if not error:
            problem_table = CLISelectTable("Add Step Problems",problems)
            while(problem_table.display()):
                pass
            selection = problem_table.last_selected
            if selection:
                form = CLIForm("Add a step:",[
                        ("Step Text: ","step_text"),
                        ("Skill 1 Name: ","skill_1_name"),
                        ("Skill 2 Name: ","skill_2_name"),
                        ("Skill 2 Name: ","skill_3_name"),
                ])
                while(form.display()):
                    pass
                                
                if form.is_complete(["step_text"]):
                    skills =[]
                    for skill in ["skill_1_name","skill_2_name","skill_3_name"]:
                        if skill in form.answers:
                            if form.answers[skill] != "":
                                skills.append(form.answers[skill])
                    
                    if skills:
                        response = self.send_blocking("tutorgen.batch_get_skill_ids",{"skill_names":skills})
                        if not "error" in response:
                            ids = response["skill_ids"]
                        else:
                            ids = {}
  
                    response = self.send_blocking("tutorgen.add_step",{"problem_id":selection[3],"step_text":form.answers["step_text"],"skill_ids":ids})
                    if not "error" in response:
                        self.print_status("Step added.")
                    else:
                        self.print_error(response["error"])
                    
                else:
                    self.print_error("Incomplete form.")
                
    def delete_step(self):
        problems,error = self._get_problems()

        if not error:
            problem_table = CLISelectTable("Delete Step Problems",problems)
            
            while(problem_table.display()):
                pass
            
            if problem_table.last_selected:
                steps,error = self._get_steps(problem_table.last_selected[-1])
                if not error:
                    step_table = CLISelectTable("Delete Step",steps)
                    while(step_table.display()):
                        pass
                    
                    step_id = step_table.last_selected[0]
                    response = self.send_blocking("tutorgen.remove_step",{"step_id":step_id})
                    if not "error" in response:
                        self.print_status("Deleted step.")
                    else:
                        self.print_error(response["error"])
                else:
                    self.print_error(error)

        else:
            self.print_error(error)
    
    def batch_load(self):
        file_input = CLIInput("Enter Filename: ")
        while(file_input.display()):
            pass
        
        problems = {}
        
        filein = open(str(file_input.answer),"r")
        for line in filein:
            if line[0] == "#" or len(line)<=3:
                continue
            
            values = [x.strip() for x in line.split(",")]
            try:
                if values[0] == "problem":
                    problem_name = values[1]
                    problem_text = values[2]
                    problems[problem_name] = {
                        "problem_text":problem_text,
                        "steps": []
                    }
                elif values[0] == "step":
                    problem = values[1]
                    step_text = values[2]
                    skills = values[3:]
                    try:
                        problems[problem]["steps"].append(
                            {
                                "step_text":step_text,
                                "skill_names":skills,
                            })
                    except KeyError:
                        self.print_error("Error in script: problem " + str(problem) + " not defined yet for step " + str(step_text))
                        return
                        
                    
                else:
                    self.print_error("Error in script: invalid start of line " + str(values[0]))
                    return
            except IndexError:
                self.print_error("Error in script: invalid fields in line " + line)
                
        for problem in problems:
            
            response = self.send_blocking("tutorgen.add_problem",{"problem_name":problem,"problem_text":problems[problem]["problem_text"]})
            if "error" in response:
                self.print_error(response["error"])
            else:                    
                self.print_status("Added problem " + problem + ".")
                
                problem_id = response["problem_id"]
                for step in problems[problem]["steps"]:
                    
                    response = self.send_blocking("tutorgen.batch_get_skill_ids",{"skill_names":step["skill_names"]})
                    if not "error" in response:
                        ids = response["skill_ids"]
                    else:
                        ids = {}
                        
                        
                    response = self.send_blocking("tutorgen.add_step",{"problem_id":problem_id,"step_text":step["step_text"],"skill_ids":ids})
                    if not "error" in response:
                        self.print_status("Added step " + step["step_text"] +".") 
                
            
                
                
                
    
    def main_callback(self):
        return True
        
    
        
        
        
        
        
        
        
if __name__ == "__main__":
    """
    table_records = []
    
    def display_table():
        table = CLITable("Select a record:",table_records)
        while(table.display()):
            pass
    
    def add_record():
        global table_records
        form = CLIForm("Enter a record:",[
                ("What is your first name?","first_name"),
                ("What is your last name?","last_name"),
                ("What is your age?","age"),
        ])
        while(form.display()):
            pass
        
        if all(k in form.answers for k in ("first_name", "last_name","age") ):
            table_records.append([form.answers["first_name"],form.answers["last_name"],form.answers["age"]])
        else:
            form.print_error("Missing values in form entry.")
    
    cb = CLIBoolean("Are you ready?")    
    while(cb.display()):
        pass
    if cb.answer:
        menu = CLIMenu("Main Menu",[
                ("Add Record",add_record),
                ("Display Table",display_table)
        ])
        
        while(menu.display()):
            pass
    
    """
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
    
    pa = ProblemAdmin(entity_id, app_secret, logger)
    signal.signal(signal.SIGTERM, pa.disconnect)
    pa.set_hpit_root_url(url_root)

    #main loops
    pa.connect()
    try:
        while(pa.main_menu.display()):
            pass
    except (KeyboardInterrupt, Exception) as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(exc_type,exc_value)
        traceback.print_tb(exc_traceback)
    pa.disconnect()  
    
