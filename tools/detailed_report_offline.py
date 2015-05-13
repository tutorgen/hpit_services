import json
import sys
from pymongo import MongoClient
from datetime import datetime,timedelta

def detailed_report(start_time,end_time):

    try:

        report_start = datetime.now()
                
        try:
            start_year = int(start_time[:4])
            start_month = int(start_time[4:6])
            start_day = int(start_time[6:])
            end_year = int(end_time[:4])
            end_month = int(end_time[4:6])
            end_day = int(end_time[6:])
        except:
            return "Error in arguments"
            
        rows = []
        peak_times = []
        end_day = datetime(end_year,end_month,end_day)
        current_day = datetime(start_year,start_month,start_day)
        one_day = timedelta(days=1)
        two_hours = timedelta(hours=2)
        
        mongo = MongoClient()
        db = mongo["hpit_development"]
        
        while current_day < end_day:
            print(str(current_day))
            date_string = datetime.strftime(current_day,"%m/%d %I%p")
            
            responses = db.sent_responses.find({
                    "message.time_created":{
                        "$gt":current_day,
                        "$lt":current_day + two_hours
                     }
            })
            
            total_responses = responses.count() 
                
            total_time = timedelta()
            for r in responses:
                time = r["time_response_received"] - r["message"]["time_created"]
                total_time += time
            
            if total_responses>0:
                avg = total_time.seconds / total_responses
            else:
                avg = 0
            
            if total_responses > 1000:
                peak_times.append((date_string,int(total_responses),float((total_responses/2)/60), float(avg)))
            
            rows.append((date_string,int(total_responses),str(total_time),float(avg)))
            current_day = current_day + two_hours
            
        report_end = datetime.now()
        report_time = ((report_end-report_start).seconds) / 60
    
        return json.dumps({"rows":rows,"peak_times":peak_times,"report_time":report_time})
    except Exception as e:
        return json.dumps({"rows":[],"peak_times":[], "report_time":-1,"error":str(e)})
    
if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("Usage: python detailed_report_offline.py YYYYMMDD YYYYMMDD")
    else:
        print(detailed_report(sys.argv[1],sys.argv[2]))
        
    
