#couldnt get this thing to work
#!/usr/bin/env python
import sys
import sqlite3 as lite
import requests
import time
from BeautifulSoup import BeautifulSoup
reservoirs = ['Alamatti','Bhadra','Ghataprabha','Harangi','Hemavathi','K.R.S','Kabini','Linganamakki','Malaprabha','Narayanapura','Supa','Tungabhadra','Varahi']
#weeks = [1]
year = 2014
week = 1


for week in range(3,53): 
    for reservoir in reservoirs:
        con = lite.connect('./database/reservoir.sqlite')
        cur = con.cursor()
        access_url = "http://www.ksndmc.org/Reservoir_Details.aspx"
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
        if len(tables) > 0:
            for k in range(0, len(tables[0].contents)):
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
                try:
                    UNIQUE_KEY = str(reservoir)+"_"+str(year)+"_"+str(week)+str(columns[1])
                    insert_data = {"RESERVOIR":reservoir , "YEAR":str(year) , "WEEK_NO":str(week)  , "FLOW_DATE":columns[1] , "PRESENT_STORAGE_TMC":columns[2] , "RES_LEVEL_FT":columns[3] , "INFLOW_CUSECS":columns[4] , "OUTFLOW_CUECS":columns[5],"UNIQUE_KEY":UNIQUE_KEY }
                    print insert_data
                    cur.execute('INSERT INTO reservoir_details (RESERVOIR , YEAR , WEEK_NO  , FLOW_DATE , PRESENT_STORAGE_TMC , RES_LEVEL_FT , INFLOW_CUSECS , OUTFLOW_CUECS,UNIQUE_KEY) VALUES (:RESERVOIR , :YEAR , :WEEK_NO  , :FLOW_DATE , :PRESENT_STORAGE_TMC , :RES_LEVEL_FT , :INFLOW_CUSECS , :OUTFLOW_CUECS, :UNIQUE_KEY)', insert_data)
                    con.commit()
                except lite.IntegrityError:
                    print 'Duplicate, couldnt add'
            else:
                print "**************** NOTHING RETURNED *********************"
        con.close()


