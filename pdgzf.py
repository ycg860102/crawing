# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 16:12:35 2018

@author: yangchg
"""
import requests, json, time, sys,datetime,os
from bs4 import BeautifulSoup
from contextlib import closing
import pandas as pd 

class pdgzfDownloader():
    
    def __init__(self, url):
        self.server = 'http://select.pdgzf.com/'
        self.url = url
        self.headers = {#'Host': "rent.pdgzf.com",
                        #'Connection': "keep-alive",
                        #'Content-Length': "110",
                        #'Origin': "http://select.pdgzf.com",
                        #'nonce': "QVLC8BOGEH8HDAYBBV3D6A94TH13NGR2",
                        'nonce': "123456",
                        #'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                        'Content-Type': "application/x-www-form-urlencoded",
                        #'Accept': "application/json, text/plain, */*",
                        #'timestamp': "QL9S5UNEN1KX4SZM2OE8ERNSRH41D5WT",
                        'timestamp': "123456",
                        #'signature': "GOLSM5PIGOUBWJK3WR84CFMTIX1JOQ4D",
                        'signature': "123",
                        #'token': "OE7TL48OBKGLTFSVY4CGP9B5JDVH5M5Z",
                        'token': "123",
                        #'Referer': "http://select.pdgzf.com/villageLists",
                        #'Accept-Encoding': "gzip, deflate",
                        #'Accept-Language': "zh-CN,zh;q=0.9",
                         }
        #self.s = requests.session()

    def getAreaUrl(self):
        req = requests.get(url=self.url, headers=self.headers)
        html = BeautifulSoup(req.text)
        urllist = html.find_all("div",attrs={"data-role":"ershoufang"})
        divs = BeautifulSoup(str(urllist[0]))
        pddivs = BeautifulSoup(str(divs.findAll('div')[2]))
        alla = pddivs.find_all('a')
        urls = {url.string:self.server+url.get('href') for url in alla }
        return urls 
    
    def getUrlsByStreet(self,url):
        req = requests.get(url=url, headers=self.headers)
        html = BeautifulSoup(req.text)
        pagebox = html.find_all("div",class_="page-box house-lst-page-box")
        totalPage = json.loads(pagebox[0].get('page-data'))['totalPage']
        urls = [url+'pg'+str(pageID) for pageID in range(2,totalPage+1)]
        return urls
        
    def getContext(self,url):
        data = "QueryJson%5BType%5D=1&QueryJson%5BKeyWord%5D=&QueryJson%5BAreaId%5D=&QueryJson%5BRoomState%5D=1&Page=1&Rows=10"
        #data = 'QueryJson%5BType%5D=5&QueryJson%5BKeyWord%5D=&QueryJson%5BAreaId%5D=&QueryJson%5BPropertyId%5D=&QueryJson%5BRoomTypeName%5D=&QueryJson%5BRental%5D=&Page=1&Rows=10'
        req = requests.post(url,data=data,headers=self.headers)
        #html = BeautifulSoup(req.text)
        return req.text
         
    

if __name__ == '__main__':
    
    now = datetime.datetime.now()
    today = now.strftime('%Y%m%d')
    
    if os.path.exists("pdgzf.xlsx") and os.access("pdgzf.xlsx",os.R_OK):
        beforeData = pd.read_excel("pdgzf.xlsx")
    else:
        #pd.DataFrame().to_excel("pdgzf.xlsx")
        beforeData = None
        
    url = 'http://rent.pdgzf.com/api/PStruct/QueryGZFPStruct'
    downloader = pdgzfDownloader(url)
    context = downloader.getContext(url)
    jsonData = json.loads(context).get('Data',None)
    if jsonData :
        rows = jsonData.get('Rows',None)
        if rows :
            dfData = pd.DataFrame(rows)
            cols = ['name','roomcount','townshipname']
            dfData = dfData[cols]
            if not beforeData :
                newHouseSet = set(dfData.name).difference(set(beforeData.name))
                newHouseinfo = dfData[dfData.name.isin(newHouseSet)]
            else :
                newHouseinfo = dfData
            dfData[cols].to_excel("pdgzf.xlsx")
            
            


    #allDataFrame.describe()
    
            
    