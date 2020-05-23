import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import datetime 
from bs4 import BeautifulSoup
import urllib
import requests
import json
import time
import csv
import pandas as pd
import sqlite3
import re
import numpy as np
from plotly.subplots import make_subplots
import plotly
import plotly.offline as py
import plotly.express as px
import plotly.graph_objs as go
import os 

listname=[]
liststock=[]
listlow=[]
listhigh=[]
listname1=[]
listclose=[]
listopen=[]
listdlow=[]
listdhigh=[]
#create a date variable for the whole program, let the user know what day is the date of use for better future reference
dateofinvestment=str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d-%H-%M"))
#the directory of the code
original_directory=os.getcwd()
#the directory of the outputfile 
newdirectory=original_directory+'/outputfile'


#first function consists the web scraping code for yahoo finance, get back the current price, previous close/open price, daylow and high and store these variables in a dataframe

def yourprofile():
    #url of the yahoo finance 
    url='https://finance.yahoo.com/quote/'
    while True:
        #enable the user to enter the tickers
        ur=input('Which stock do you want to look into today?(Please enter a valid Ticker Symbol, enter done to proceed to next section\n')
        #enter done will quit the loop and move to the nexr section
        if ur.upper()=='DONE':
            print('Ok, let\' move to the next part.')
            #break out the loop 
            break
        #if the user didn't enter done, user enter tickers will be put togehter and form the url of the specific target webpage
        finalurl=url+ur.upper()+'?p='+ur.upper()+'&.tsrc=fin-srch'
        #beautifulsoup 
        r=requests.get(finalurl)
        soup = BeautifulSoup(r.content,'lxml')

        #use try/exceot to catch if theres any error, if user entered an invalid ticker(ie, the webpage does not exist, the code will catch it and ask for another input)
        try:
            #fetch the information 
            stockprice=soup.find_all('div',{"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find('span').text
            companyinfo=soup.find_all('h1')[0]
            lowandhigh=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[5].text
            lowandhighdaily=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[4].text
            previousclose=soup.find_all('tr',{'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[0].find_all('td')[1].text 
            openvalue=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[1].text
        #except catch the unvalid ticker info
        except:
            print('The information you entered seems like an unvalid ticker.')
            continue
        # if for some reason the webpage exist, but there is no data on it to fetch, it will tell the user.
        if soup.find_all('tr',{'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[0].find_all('td')[1].text =='N/A':
            print ('Website can\'t fetch, please try a different ticker.')
            continue 
        
        #after we get the required information, next is data cleaning 
        range1=lowandhigh.split('- ')
        low=range1[0]
        high=range1[1]
        # print out a current price response statement to the user 
        response=ur.upper()+' Current Price'+': '+str(stockprice) 
        print(response+' Fifty-Two weeks low: '+low + ' Fifty-Two weeks high:'+ high)
        companyinfo=companyinfo.contents
        str1=''
        str2=str1.join(companyinfo)
        str4=str2.find('- ')+2
        str3=str2[str4:].replace(' ','-' )
        str3=str3.replace(',','')
        rangedaily=lowandhighdaily.split('- ')
        lowdaily=rangedaily[0]
        highdaily=rangedaily[1]
        listname.append(ur.upper())
        # data was originally in string and european form, it needs to be cast into float for data visualization later.
        liststock.append(float(re.sub("[^\d\.]", "", stockprice)))
        listlow.append(float(re.sub("[^\d\.]", "", low)))
        listhigh.append(float(re.sub("[^\d\.]", "", high)))
        listname1.append(str3)
        listclose.append(float(re.sub("[^\d\.]", "",previousclose)))
        listopen.append(float(re.sub("[^\d\.]", "",openvalue)))
        listdlow.append(float(re.sub("[^\d\.]", "", lowdaily)))
        listdhigh.append(float(re.sub("[^\d\.]", "", highdaily)))
    global userselection
    #from the information i get, store them into a data frame
    userselection=pd.DataFrame({'Symbol':listname,'Price':liststock,'Previous Close ':listclose,'Open Price ':listopen,'52 week low':listlow,'52 week high':listhigh,'Daily High ':listdhigh,'Daily Low ':listdlow})
    userselection.drop_duplicates(subset='Symbol',keep='first',inplace=True)
    #change the directory, and output the file to outputfile folder
    os.chdir(newdirectory)
    userselection.to_csv('YourSelection'+dateofinvestment+'.csv')
    os.chdir(original_directory)
    return userselection,listname,liststock,listlow,listhigh,listname1,listclose,listopen,listdlow,listdhigh




#data visualization of the stocks (user input)
#first function is to get allt he required data, I scraped the weekly close price from Yahoo Finance. 
def graphhistoricaltrend():
    v1=[]
    v2=[]
    for i in listname:
        urlgraph='https://finance.yahoo.com/quote/'+i+'/history?period1=1557199116&period2=1588821516&interval=1wk&filter=history&frequency=1wk'
        rgraph=requests.get(urlgraph)
        soup=BeautifulSoup(rgraph.content,'lxml')
        #all weekly closeprice
        graph1=soup.find_all('td',"Py(10px) Pstart(10px)")
        #the corresponding date 
        dategraph=soup.find_all('td','Py(10px) Ta(start) Pend(10px)')   
        #append the length of each ticker
        v1.append(len(graph1))
        v2.append((len(dategraph)))   
        global v3
        global v4
        #find out the minimum of them 
        v3=int(min(v1))
        v4=int(min(v2))
        return v3,v4

t1=[]
t2=[]


# from the graphhistoricaltrend() result, we can now plot the graph 
def graphhistoricaltrend2():
    fig=go.Figure()
    graphhistoricaltrend()
    listnamenoduplicate=list(set(listname))
    for i in range(len(listnamenoduplicate)):
        urlgraph='https://finance.yahoo.com/quote/'+listnamenoduplicate[i]+'/history?period1=1557199116&period2=1588821516&interval=1wk&filter=history&frequency=1wk'
        rgraph=requests.get(urlgraph)
        soup=BeautifulSoup(rgraph.content,'lxml')
        graph1=soup.find_all('td',"Py(10px) Pstart(10px)")
        dategraph=soup.find_all('td','Py(10px) Ta(start) Pend(10px)')
        graphdate=[]
        graphclose=[]
        for item in range(int(v3/6)):
            graphdate.append(datetime.datetime.strptime(dategraph[item].text,'%b %d, %Y'))   
        item=3
        while item<=v3:
            try:
                graphclose.append(float(re.sub("[^\d\.]", "",graph1[item].text)))
            except:
                graphclose.append(0)
            item+=6

        #interactive graph 
        fig.add_trace(go.Scatter(x=graphdate, y=graphclose, mode='lines+markers',showlegend=True,name=listnamenoduplicate[i]))
        fig.update_layout(title='Historical Weekly Trend of the Tickers',xaxis_title="Date",yaxis_title="Close Price",)
    fig.show()
    os.chdir(newdirectory)
    fig.write_html(dateofinvestment+'.html')
    os.chdir(original_directory)

#interactive plot for recommending tickers
#def graphhistoricaltrend2forrecommend(l3)

def graphhistoricaltrend2forrecommend(l3,rectype):
    fig=go.Figure()
    graphhistoricaltrend()
    listnamenoduplicate=list(set(l3))
    for i in range(len(listnamenoduplicate)):
        urlgraph='https://finance.yahoo.com/quote/'+l3[i]+'/history?period1=1557199116&period2=1588821516&interval=1wk&filter=history&frequency=1wk'
        rgraph=requests.get(urlgraph)
        soup=BeautifulSoup(rgraph.content,'lxml')
        graph1=soup.find_all('td',"Py(10px) Pstart(10px)")
        dategraph=soup.find_all('td','Py(10px) Ta(start) Pend(10px)')
        graphdate=[]
        graphclose=[]
        try:
        	for item in range(int(v3/6)):
        		graphdate.append(datetime.datetime.strptime(dategraph[item].text,'%b %d, %Y'))  
        	item=3
        	while item <= v3:
        		graphclose.append(float(re.sub("[^\d\.]", "",graph1[item].text)))
        		item+=6

        except:
        	continue
        fig.add_trace(go.Scatter(x=graphdate, y=graphclose, mode='lines+markers',showlegend=True,name=listnamenoduplicate[i]))
        #fig.update_layout(title='Historical Trend of the recommending Stocks',xaxis_title="Date",yaxis_title="Close Price",)
        fig.update_layout(title='Historical Trend of the'+rectype+ 'Stocks',xaxis_title="Date",yaxis_title="Close Price",)
    fig.show()
    os.chdir(newdirectory)
    fig.write_html(dateofinvestment+'Rec'+rectype+'.html')
    os.chdir(original_directory)




#fucntion that returns average of a list
def average(l5):
    if len(l5) == 0:
        return 0
    else:
        return sum(l5)/len(l5)




g1=[]
g2=[]
g3=[]
g4=[]
g5=[]
g6=[]
g7=[]
g8=[]

#move to recommendation part 
#webscraping the daily gainer tickers 

def dailygainer():
    url4='https://finance.yahoo.com/gainers'
    r4=requests.get(url4)
    soup=BeautifulSoup(r4.content,'lxml')
    gains=soup.find_all('a',{"Fw(600)"})
    gains2=soup.find_all('td',{"Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)"}) 
    for item in range(len(gains)):
        g1.append(gains[item].text)
        g2.append(gains[item].attrs['title'])
    item=0
    item1=1
    item2=2
    while item < len(gains2):
        g3.append(gains2[item].text)
        g4.append(gains2[item+1].text)
        g5.append(gains2[item+2].text)
        item=item+3
    for i in g3: 
        g6.append(float(re.sub("[^\d\.]", "", i)))
    for i in g4:
        g7.append(float(re.sub("[^\d\.]", "", i)))
    for i in g5:
        g8.append(float(re.sub("[^\d\.]", "", i)))

    dailygainer1=pd.DataFrame({'Symbol':g1,'Name':g2,'Price':g6,'Change':g7,'Percent_Change':g8})
    #visualize the top ten gainer stocks for today 
    dailygainer1=dailygainer1[:10]
    df = dailygainer1.sort_values(by='Percent_Change', ascending=True)
    data  = go.Data([go.Bar(y=df.Symbol, x = df.Percent_Change,orientation='h')])
    layout = go.Layout(title = "Top 10 Daily Gainer Stocks "+ dateofinvestment)
    fig  = go.Figure(data=data, layout=layout)
    py.plot(fig)
    os.chdir(newdirectory)
    fig.write_html(dateofinvestment+'top10gainers.html')
    os.chdir(original_directory)
    #fig.show()
    return dailygainer1,g1,g2,g3,g4,g5,g6,g7,g8

#output them and updata to a csv file 
def gainerstockcsv():
    dailygainer()
    dt1=str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d-%H-%M"))
    with open('Gainer1.csv','a+',newline="") as csv_file:
        writer = csv.writer(csv_file)
        #writer.writerow(['Symbol','Name','Last Price','Change','Percent of Change','Time'])
        for i in range(len(g1)):
            writer.writerow([g1[i],g2[i],g3[i],g4[i],g5[i],dt1[:16]])     

dt1=str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d-%H-%M"))
resultgainer=[]


def getsql2(filename):
    conn = sqlite3.connect('Gainer.db')
    c = conn.cursor()
    #dt1=str(datetime.datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d-%H-%M"))
    c.execute("DROP TABLE IF EXISTS Gainer_dataset")
    c.execute('''CREATE TABLE Gainer_dataset (Symbol TEXT,Name TEXT,Last Price TEXT,Change TEXT,Percent_of_Change Real,Time Text)''')
    with open(filename) as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',') 
        for i in (csv_reader):
            c.execute("INSERT INTO Gainer_dataset VALUES (?,?,?,?,?,?)", i)
            c.execute("SELECT * FROM Gainer_dataset WHERE Time Like '2020-05%' Order by Random() Limit 5")
        for row in c.fetchall():
            resultgainer.append(row)
    return (resultgainer)

#similar function as before, randomly pick out tickers from the past database(live, scrape it everyday.
def recommendtickers(l1,rectype):
    listnamerec=[]
    liststockrec=[]
    listlowrec=[]
    listhighrec=[]
    listname1rec=[]
    listcloserec=[]
    listopenrec=[]
    listdlowrec=[]
    listdhighrec=[]
    for i in l1:
        url6='https://finance.yahoo.com/quote/'
        finalurl6=url6+i+'?p='+i+'&.tsrc=fin-srch'
        rrec=requests.get(finalurl6)
        soup = BeautifulSoup(rrec.content,'lxml')
        try:
            stockpricerec=soup.find_all('div',{"My(6px) Pos(r) smartphone_Mt(6px)"})[0].find('span').text
            companyinforec=soup.find_all('h1')[0]
            lowandhighrec=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[5].text
            lowandhighdailyrec=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[4].text
            previouscloserec=soup.find_all('tr',{'Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($seperatorColor) H(36px)'})[0].find_all('td')[1].text 
            openvaluerec=soup.find_all('td',{"Ta(end) Fw(600) Lh(14px)"})[1].text
            
            rec1=lowandhighrec.split('- ')
            lowrec=rec1[0]
            highrec=rec1[1]
            responserec=i+' Current Price'+': '+str(stockpricerec) 
            print(responserec+' Fifty-Two weeks low: '+lowrec + ' Fifty-Two weeks high:'+ highrec)
            companyinforec=companyinforec.contents
            str1rec=''
            str2rec=str1rec.join(companyinforec)
            str4rec=str2rec.find('- ')+2
            str3rec=str2rec[str4rec:].replace(' ','-' )
            str3rec=str3rec.replace(',','')
            rangedailyrec=lowandhighdailyrec.split('- ')
            lowdailyrec=rangedailyrec[0]
            highdailyrec=rangedailyrec[1]
            listnamerec.append(i)
            liststockrec.append(float(re.sub("[^\d\.]", "", stockpricerec)))
            listlowrec.append(float(re.sub("[^\d\.]", "", lowrec)))
            listhighrec.append(float(re.sub("[^\d\.]", "", highrec)))
            listname1rec.append(str3rec)
            listcloserec.append(float(re.sub("[^\d\.]", "",previouscloserec)))
            listopenrec.append(float(re.sub("[^\d\.]", "",openvaluerec)))
            listdlowrec.append(float(re.sub("[^\d\.]", "", lowdailyrec)))
            listdhighrec.append(float(re.sub("[^\d\.]", "", highdailyrec)))
        except:
            print('Website can\'t fetch,continue to next ticker')
            continue      
        
    userselectionrec=pd.DataFrame({'Symbol':listnamerec,'Price':liststockrec,'Previous Close ':listcloserec,'Open Price ':listopenrec,'52 week low':listlowrec,'52 week high':listhighrec,'Daily High ':listdhighrec,'Daily Low ':listdlowrec})
    os.chdir(newdirectory)
    with open('Recommend'+dateofinvestment+'.csv', 'a') as f:
        userselectionrec.to_csv(f, header=False)
    os.chdir(original_directory)
    graphhistoricaltrend2forrecommend(listnamerec,rectype)



Symbol=[]
Name=[]
LP=[]
CHG=[]
PCHG=[]
Volume=[]
trendlist=[]
trendadict=dict()
result=[]
url2='https://finance.yahoo.com/trending-tickers'
#web scrape the trending tickers
def TrendingT():
    r=requests.get(url2)
    soup = BeautifulSoup(r.content,'lxml')
    trend=soup.find_all('a',{'Fw(b)'})
    trend1=soup.find_all('td',{"data-col2 Ta(end) Pstart(20px)"})
    trend2=soup.find_all('td',{"data-col4 Ta(end) Pstart(20px)"})
    trend3=soup.find_all('td',{"data-col5 Ta(end) Pstart(20px)"})
    trend4=soup.find_all('td',{"data-col6 Ta(end) Pstart(20px)"})
    for item in range(len(trend1)):
        trenddict=dict()
        Symbol.append(trend[item].attrs['data-symbol'])
        Name.append(trend[item].attrs['title'])
        LP.append(trend1[item].text) 
        CHG.append(trend2[item].find('span').text)    
        PCHG.append(trend3[item].find('span').text)
        Volume.append(trend4[item].text)   
    trenddict['Symbol']=Symbol
    trenddict['Name']=Name
    trenddict['Last Price']=LP
    trenddict['Change']=CHG
    trenddict['Percent of Change']=PCHG
    trenddict['Volume']=Volume                        
    Trending=pd.DataFrame({'Symbol':Symbol,'Name':Name,'Last Price':LP,'Change':CHG,'Percent_Change':PCHG,'Volume':Volume})
    print(Trending.sample(n=5))
    #Trending.plot.bar()
    #return Trending
    return Symbol,Name,LP,CHG,PCHG,Volume

def trendstockcsv():
    TrendingT()
    with open('Trending1.csv','a+',newline="") as csv_file:
        writer = csv.writer(csv_file)
        #writer.writerow(['Symbol','Name','Last Price','Change','Percent of Change','Volume','Time'])
        for i in range(len(Symbol)):
            writer.writerow([Symbol[i],Name[i],LP[i],CHG[i],PCHG[i],Volume[i],dt1[:16]])   

#trendstockcsv()

resulttrending=[]
def getsql(filename):
    
    conn = sqlite3.connect('Trending.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS Trending_dataset')
    #resulttrending=[]
    
    c.execute('''CREATE TABLE Trending_dataset (Symbol TEXT,Name TEXT,Last Price TEXT,Change TEXT,Percent_of_Change TEXT,Volume TEXT,Time Text)''')
    with open(filename) as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',') 
        #next(csv_reader)
        for i in (csv_reader):
            c.execute("INSERT INTO Trending_dataset VALUES (?,?,?,?,?,?,?)", i)
            if finalanswer==1:
                c.execute("SELECT * FROM Trending_dataset WHERE Time Like '2020-%' Order by Random() Limit 5")
            else: 
                c.execute("SELECT * FROM Trending_dataset WHERE Time Like '2020-%' and Percent_of_Change Like'+%' Order by Random() Limit 5")
            #c.execute("SELECT * FROM Gainer_dataset WHERE Time Like '2020-05%' Order by Random() Limit 3")
        for row in c.fetchall():
            resulttrending.append(row)
    return (resulttrending)  


#the function to recommend stocks based to gainer and trending tickers in the past
def recommendprofile():
    while True:
        inputforrecommend=input('Now you have already put in your interested stocks in the system. \n Next we will recommend you a few tickers based on the gainer and trending tickers we scraped real time and what we scraped and stored in our database.\n Please answer the following question. \n Are you a high risk taker ?(Enter Yes or No)\n')
        validanswer=['YES','NO']
        if inputforrecommend.upper() in validanswer:
            if inputforrecommend.upper()=='YES':
                global finalanswer
                finalanswer=1
                break
            else:
                finalanswer=2
                break
        else:
            print('Invalid input, please answer Yes or No')
    gainerstockcsv()
    getsql2('Gainer1.csv')
    resultgainer2=[]
    #show the result to the user
    for i in range(len(resultgainer)):
        resultgainer2.append(resultgainer[i][0])
    #plot the interactive graph
    print('These are the recommend Gainer Tickers')
    print(recommendtickers(resultgainer2,' Gainer '))
    trendstockcsv()
    getsql('Trending1.csv')
    resulttrending2=[]
    for i in range(len(resulttrending)):
        resulttrending2.append(resulttrending[i][0])
    print('These are the recommend Trending Tickers')
    print(recommendtickers(resulttrending2,' Trending '))


#get the company happiness rating 
def indeedJob(companyname,ticker):
    WorkHappiness=[]
    Achievement=[]
    Learning=[]
    tic=[]
    name=[]
    url='https://www.indeed.com/cmp/'
    #non US company and small firm might not have a happiness rating yet. 
    print('Some of the companies may not have a work happiness rating yet')
    print('Below is only showing the company with a rating')
    print(range(len(companyname)))
    for i in range(len(companyname)):
        furl=url+companyname[i]
        print(furl)
        r=requests.get(furl)
        soup = BeautifulSoup(r.content,'lxml')
        happiness=soup.find_all('div', {'cmp-DetailedHappiness-scoreSection'},{'cmp-HappinessScoreBox cmp-DetailedHappiness-score'})
        #if the company has a rating, scrape them and put them into the dataframe
        if len(happiness) != 0 :
            name.append(companyname[i])
            tic.append(str(ticker[i]).strip())
        for i in range(len(happiness)):
            if i ==0:
                WorkHappiness.append(float(re.sub("[^\d\.]", "",happiness[i].text)))
            elif i==1:
                Achievement.append(float(re.sub("[^\d\.]", "",happiness[i].text)))
            elif i==2:
                Learning.append(float(re.sub("[^\d\.]", "",happiness[i].text)))
                global JobSatisf
                JobSatisf=pd.DataFrame({'Company_Ticker': tic,'Company_Name': name,'Work_Happiness_Rating':WorkHappiness,'Acievement_Rating':Achievement,'Learning_Rating':Learning})
        else:
            JobSatisf=pd.DataFrame({'Company_Ticker':tic,'Company_Name': name,'Work_Happiness_Rating':WorkHappiness,'Acievement_Rating':Achievement,'Learning_Rating':Learning})
    #when there is availabe information, plot a bar chart.
    try:  
        barWidth = 0.15
        r1 = np.arange(len(WorkHappiness))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        plt.bar(r1, WorkHappiness, color='#ED9F30', width=barWidth, edgecolor='white', label='Work_Happiness_Rating')
        plt.bar(r2, Achievement, color='#B7D7D7', width=barWidth, edgecolor='white', label='Acievement_Rating')
        plt.bar(r3, Learning, color='#859091', width=barWidth, edgecolor='white', label='Learning_Rating')
        plt.xlabel('Companies', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(WorkHappiness))], name)
        plt.legend()
        plt.show(block=False)
        #plt.savefig('workinghappiness.png')

        #print(JobSatisf)
        whavg=average(WorkHappiness)
        achavg=average(Achievement)
        leaavg=average(Learning)
    
        #create a new column, if the rating fo the company is below average, then it is not satisfiable 
        JobSatisf.loc[JobSatisf['Work_Happiness_Rating']>=whavg, 'WH_Match'] = 'Satisfied'
        JobSatisf.loc[JobSatisf['Work_Happiness_Rating']<whavg, 'WH_Match'] = 'Not Satisfied'
    
        JobSatisf.loc[JobSatisf['Acievement_Rating']>=achavg, 'AC_Match'] = 'Satisfied'
        JobSatisf.loc[JobSatisf['Acievement_Rating']<achavg, 'AC_Match'] = 'Not Satisfied'
    
        JobSatisf.loc[JobSatisf['Learning_Rating']>=leaavg, 'LE_Match'] = 'Satisfied'
        JobSatisf.loc[JobSatisf['Learning_Rating']<leaavg, 'LE_Match'] = 'Not Satisfied'
    except:
        print('No Graph and Data is available for the companies of your choice')

    print(JobSatisf)
    return JobSatisf,WorkHappiness,Achievement,Learning



#use nyt api to get the relevant news about your searched company 

#print('Last, here is some related news(highlight) about the company, the url is also attached so you can check the full contents as well.')
def nytnews(keyword,accesskey):
    for i in range(len(keyword)):
        print('Recent News about '+keyword[i] +'\n')
        web='https://api.nytimes.com/svc/search/v2/articlesearch.json?q='+keyword[i]+'&api-key='+accesskey 
        resp=requests.get(web)
        js = resp.json()
        #for i in range(1):
        title=js['response']['docs'][0]['abstract']
        paragraph=js['response']['docs'][0]['lead_paragraph']
        newsurl=js['response']['docs'][0]['web_url']
        #print out the title \, highlight, and url 
        print(title,paragraph,newsurl)
    
        
#listnamenews=list(set(listname1))
#nytnews(listnamenews,'LXQIHhj7QMNmxphtxeEeGGZ3SLMpWKt9')
growthrate1=[]
growthrate2=[]
forecastrate=[]

#function for stock analysis
def stockgrowth(l7):
    for i in range(len(l7)):
        urlanalysis='https://finance.yahoo.com/quote/'+l7[i]+'/analysis?p='+l7[i]
        ranalysis=requests.get(urlanalysis)
        soup = BeautifulSoup(ranalysis.content,'lxml')
        growth=soup.find_all('td', {'Ta(end) Py(10px)'})
        try:
            growthrate1.append(float((growth[0].text).replace('%','').replace(',','')))
            growthrate2.append(float((growth[4].text).replace('%','').replace(',','')))
            if float((growth[0].text).replace('%','')) < 0 and float((growth[4].text).replace('%',''))>0:     
                forecastrate.append(round(((float((growth[4].text).replace('%',''))-float((growth[0].text).replace('%','')))/float((growth[0].text).replace('%','')))*-100,2))
            else:
                forecastrate.append(round(((float((growth[4].text).replace('%',''))-float((growth[0].text).replace('%','')))/float((growth[0].text).replace('%','')))*100,2))
        
            #forecastrate.append(round((float((growth[4].text).replace('%','').replace(',',''))-float((growth[0].text).replace('%','').replace(',','')))/float((growth[0].text).replace('%','').replace(',',''))*100,2))
        except:
            continue

        #forecastrate.append(round((float((growth[4].text).replace('%','').replace(',',''))-float((growth[0].text).replace('%','').replace(',','')))/float((growth[0].text).replace('%','').replace(',',''))*100,2))
    stockgrowthrate=pd.DataFrame({'Company_Ticker':l7,'current_quarter': growthrate1,'Next_quarter':growthrate2,'Growth_Rate':forecastrate})
    for i in range(len(l7)):
        print(l7[i]+' growth estimate for current quarter is to be '+ str(growthrate1[i])+'%. Next Quarter is estimate to be '+str(growthrate2[i])+'%. Based on the calcualation, there is a '+str(forecastrate[i])+'% Change.')
    
    stockgrowthrate['Company_Ticker'] = stockgrowthrate['Company_Ticker'].astype(str)
    JobSatisf['Company_Ticker'] = JobSatisf['Company_Ticker'].astype(str)
    try:
        stockgrowthrate1=pd.merge(stockgrowthrate,JobSatisf,on='Company_Ticker')
        #merge the dataframe with the growthrate and jab satisfied, and print it out to the user.
        print(stockgrowthrate1)
        #plot work happiness rating with growth rage change
        figanalysis = px.bar(stockgrowthrate1, x="Company_Name", y='Growth_Rate',hover_data=['current_quarter', 'Next_quarter'],color='Work_Happiness_Rating',labels={'Company_Ticker':'population of Canada'}, height=400)
        figsubplot = make_subplots(rows=3, cols=1,shared_yaxes=True)
        #plot their current rate nad next quarter rate
        figsubplot.add_trace(go.Bar(x=stockgrowthrate1.Company_Name,y=stockgrowthrate1.current_quarter,name='Current Quarter Estimate Growth Rate'),row=1,col=1)
        figsubplot.add_trace(go.Bar(x=stockgrowthrate1.Company_Name,y=stockgrowthrate1.Next_quarter,name='Next Quarter Estimate Growth Rate'),row=2,col=1)
        figsubplot.show()
        figanalysis.show()
        os.chdir(newdirectory)
        figanalysis.write_html('Growth Rate and Happiness.html')
        os.chdir(original_directory)
    except:
        print('No graph is available for the company of your choice')


#combines the function, allow user to input, check the price, and visualize. 
def investmentprofile():  
    #print and show the date to the  user
    print('It is now : '+dateofinvestment)     
    print('Welcome to your personal investment portfolio\nFirst, let\'s start by checking the prices of your interested stocks.') 
    print('Enter one ticker at a time. Enter done to finish this session.')
    yourprofile()
    print('A graph and a bar plot shows the historical closing price trend and summary of your selected stocks is prompt.')
    userselection.plot.bar()
    plt.xticks([r for r in range(len(listname))], listname)
    #plt.savefig('userselectionoverview.png')
    plt.show(block=False)
    #close the plot 
    plt.clf()
    graphhistoricaltrend2()
    #anything other than yes will interpretate as a no. 
    print ('ok let\'s move forward')
    print('Next the system will randomly recommend some gainer tickers and trending tickers for you.')   
    print('Here is a brief overview of your previous selections')
    print('Stocks')
    #show the dataframe of what user select 
    print(userselection)
    recommendprofile()
    listname1noduplication=list(set(listname1))
    listtickernoduplication=list(set(listname))
    indeedJob(listname1noduplication,listtickernoduplication)
    print('It is interesting to learn about the company culture. It often reflects a company\'s value')
    print('The following is the indeed work happiness rating for the company you selected.')
    print('We will companre it with the company\'s growth rate')
    

    stockgrowth(listname)

   #indeedJob(listname1noduplication)
    print('Last, here is some related news(highlight) about the company, the url is also attached so you can check the full contents as well.')
    listnamenews=list(set(listname1))
    nytnews(listnamenews,'enter your api access code')
    print('Finished, your selections and recommendations are saved in directory folders. Have a nice Day! ')

#call the function         
investmentprofile()
