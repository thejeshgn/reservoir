#couldnt get this thing to work
#!/usr/bin/env python
import sys
import sqlite3 as lite
import requests
import time
from BeautifulSoup import BeautifulSoup
reservoirs = ['Alamatti','Bhadra','Ghataprabha','Harangi','Hemavathi','K.R.S','Kabini','Linganamakki','Malaprabha','Narayanapura','Supa','Tungabhadra','Varahi']
#weeks = [1]
year = 2010
start_week = 1
import dataset
db = dataset.connect('sqlite:///./database/reservoir.sqlite')
reservoir_table = db['reservoir_details']
query_1 = "SELECT max(week_no) as start_week FROM reservoir_details where YEAR='"+str(year)+"'"
print query_1
result = db.query(query_1)
for row in result:
    start_week = row['start_week']

if start_week == None:
    start_week = 1

print "Starting with WEEK_NO="+str(start_week)+" of the YEAR="+str(year) 


for week in range(start_week,53): 
    print "Now for week="+str(week)
    for reservoir in reservoirs:
        reservoir_completion_status = reservoir_table.find_one(RESERVOIR=reservoir, YEAR=str(year), WEEK_NO=week)
        print "RESERVOIR ="+reservoir
        if reservoir_completion_status:
            print  "completed"
            continue
        print "Starting now"
        request_session = requests.Session()
        html_src = ""
        user_agent = {'User-agent': 'Mozilla/5.0'}
        time.sleep(30)
        html_get_src = request_session.get("http://www.ksndmc.org/Reservoir_Details.aspx",headers = user_agent)
        page = BeautifulSoup(html_get_src.text)
        __VIEWSTATE = page.find(id="__VIEWSTATE")["value"]
        __PREVIOUSPAGE = page.find(id="__PREVIOUSPAGE")["value"]
        __EVENTVALIDATION = page.find(id="__EVENTVALIDATION")["value"]
        all_coockies = requests.utils.dict_from_cookiejar(html_get_src.cookies)
        NET_SessionId = all_coockies['ASP.NET_SessionId']
        cookie = {'ASP.NET_SessionId': NET_SessionId}

        #print __VIEWSTATE
        #print __PREVIOUSPAGE
        #print __EVENTVALIDATION
        #print NET_SessionId


        payload = {
            'ctl00$cpMainContent$DropDownList1':  str(reservoir),
            'ctl00$cpMainContent$Year_list':str(year),
            'ctl00$cpMainContent$weekList': str(week),
            'ctl00$cpMainContent$Button1':'Get Details',
            "__VIEWSTATE":__VIEWSTATE,
             "__PREVIOUSPAGE":__PREVIOUSPAGE,
             "__EVENTVALIDATION":__EVENTVALIDATION,
             "__EVENTTARGET":" ",
             "__EVENTARGUMENT":" "

        }
        user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36','Referer':'https://www.ksndmc.org/Reservoir_Details.aspx','Content-Type':'application/x-www-form-urlencoded','Origin':'https://www.ksndmc.org','Host':'www.ksndmc.org','Accept-Encoding':'gzip,deflate,sdch','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}        
        html_post_src = request_session.post("https://www.ksndmc.org/Reservoir_Details.aspx",data=payload,cookies=html_get_src.cookies,headers = user_agent)
        soup = BeautifulSoup(html_post_src.content)
        tables = soup.findAll(id="ctl00_cpMainContent_GridView1")

        if len(tables) > 0 and len(tables[0].contents) > 2 :
            inserted = False
            for k in range(0, len(tables[0].contents)):
                print str(k)
                if k <= 1:
                    continue
                #ignore if not tr
                columns = []
                if getattr(tables[0].contents[k], 'name', None) == 'tr':
                    row = tables[0].contents[k]
                    for r in range(0, len(row.contents)):
                        if getattr(row.contents[r], 'name', None) == 'td': 
                            td_column = row.contents[r]
                            #print td_column
                            #print td_column
                            if len(td_column.contents[0]) > 0:                       
                                value = td_column.contents[0]
                                columns.append(value)
                            else:
                                columns.append("")
                else:
                    continue
                inserted = True
                UNIQUE_KEY = str(reservoir)+"_"+str(year)+"_"+str(week)+str(columns[1])
                insert_data = dict({"RESERVOIR":reservoir , "YEAR":str(year) , "WEEK_NO":week  , "FLOW_DATE":columns[1] , "PRESENT_STORAGE_TMC":columns[2] , "RES_LEVEL_FT":columns[3] , "INFLOW_CUSECS":columns[4] , "OUTFLOW_CUECS":columns[5],"UNIQUE_KEY":UNIQUE_KEY })
                print insert_data
                reservoir_table.insert(insert_data)
            #after the for loop if not inserted
            if inserted == False:
                print "**************** NOTHING INSERTED *********************"
                UNIQUE_KEY = str(reservoir)+"_"+str(year)+"_"+str(week)
                insert_data = dict({"RESERVOIR":reservoir , "YEAR":str(year) , "WEEK_NO":week ,"UNIQUE_KEY":UNIQUE_KEY })
                print insert_data
                reservoir_table.insert(insert_data)

        else:
            print "**************** NOTHING RETURNED *********************"
            UNIQUE_KEY = str(reservoir)+"_"+str(year)+"_"+str(week)
            insert_data = dict({"RESERVOIR":reservoir , "YEAR":str(year) , "WEEK_NO":week ,"UNIQUE_KEY":UNIQUE_KEY })
            print insert_data
            reservoir_table.insert(insert_data)

