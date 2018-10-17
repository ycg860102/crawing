# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 16:12:35 2018

@author: yangchg
"""
import requests, json, time, sys
from bs4 import BeautifulSoup
from contextlib import closing
import pandas as pd 

class lianjiaDownloader():
    
    def __init__(self, url):
        self.server = 'http://sh.lianjia.com'
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                        "Referer": "https://sh.lianjia.com/ershoufang/"}
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
        req = requests.get(url)
        html = BeautifulSoup(req.text)
        return html
        
    def contextToDict(self,context):
        #每个info clear 表示一个房子的信息，遍历当前页面上所有的info_clear
        clears = context.find_all('div',class_='info clear')
        houseDictPerPage = []
        houseLabels = ["title","houseInfo","positionInfo","followInfo","subway","taxfree","haskey","totalPrice","unitPrice"]
        for oneHouseInfos in clears :
            houseDict = {}
            oneHouseInfos = BeautifulSoup(str(oneHouseInfos))
            #print oneHouseInfos.find(class_='title').text
            for label in houseLabels:
                try :
                    houseDict[label] = oneHouseInfos.find(class_=label).text
                    
                except :
                    houseDict[label] = ''
            houseDictPerPage.append(houseDict)
        return houseDictPerPage
    

if __name__ == '__main__':
    url = 'http://sh.lianjia.com/ershoufang/pudong/'
    downloader = lianjiaDownloader(url)
    urls = downloader.getAreaUrl()
    allDatas = []
    testurl = {}
    testurl[u'塘桥'] = urls[u'塘桥']

    for key,FirstPageUrl in urls.items() :
        #爬取该URL第一页数据
        print(u'开始爬取'+key+u"街道数据：")
        context = downloader.getContext(FirstPageUrl)
        steetData = downloader.contextToDict(context)
        #根据第一页数据的总页数，生成该街道总共页数，并生成URL列表
        streetUrls = downloader.getUrlsByStreet(FirstPageUrl)
        for streeturl in streetUrls:
            print(u'开始爬取第'+streeturl+u"页数据：") 
            context = downloader.getContext(streeturl)
            steetData.extend(downloader.contextToDict(context))
            time.sleep(1)     
        steetData = pd.DataFrame(steetData) 
        steetData['street'] = key
        allDatas.append(steetData)    
    print(u'数据爬取完成！')
    
    #数据拆分和汇总，并保存到Excel中
    allDataFrame = pd.concat(allDatas)        
    allDataFrame.reset_index(inplace=True)
    houseInfo = allDataFrame['houseInfo'].str.split('|',expand=True)
    housebs = houseInfo[houseInfo[6].notna()][[x for x in range(7) if x !=1 ]]
    housebs.columns=[u'小区名称',u'格局',u'面积',u'朝向',u'装修',u'电梯']
    floolHouse= houseInfo[~houseInfo[6].notna()][range(6)]
    floolHouse.columns=[u'小区名称',u'格局',u'面积',u'朝向',u'装修',u'电梯']
    allDataFrame=allDataFrame.join(pd.concat([floolHouse,housebs]))

    positionInfo = allDataFrame['positionInfo'].str.split('-',expand=True)
    positionInfo.columns=[u'楼层',u'区域']
    allDataFrame=allDataFrame.join(positionInfo)
    allDataFrame.to_excel('allDataFrame.xlsx') 
    
    allDataFrame["totalPrice"] = allDataFrame.totalPrice.apply(lambda x : float(x.replace(u'万','')))
    allDataFrame = allDataFrame[~allDataFrame[u'面积'].apply(lambda x : u'室' in x )]
    allDataFrame[u'面积'] = allDataFrame[u'面积'].apply(lambda x :float(x.replace(u'平米','')))
    
    allDataFrame.describe()
    
            
    