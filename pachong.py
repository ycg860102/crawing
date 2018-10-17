# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 18:17:44 2018

@author: yangchg
"""

import os,sys,datetime
import requests
import json,jsonpath
import re
import pandas as pd
#from lxml import html
import mail2
import ConfigParser
sys.path.append("D:\Program Files\Tinysoft\Analyse.NET") 
reload(sys)    
sys.setdefaultencoding('utf8')
import TSLPy2


headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
#'Cookie':'sseMenuSpecial=8348; yfx_c_g_u_id_10000042=_ck18041118463217635335025415592; yfx_mr_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_mr_f_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_key_10000042=; yfx_f_l_v_t_10000042=f_t_1523443592761__r_t_1523443592761__v_t_1523443797715__r_c_0; VISITED_MENU=%5B%228350%22%2C%228349%22%2C%228353%22%2C%228355%22%2C%228359%22%2C%228352%22%5D
        'Host':'data.eastmoney.com',
        #'Referer':'http://www.sse.com.cn/disclosure/listedinfo/loss/',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

def sendMail(filepath):
    subject = u'上市公司公告信息'
    text = u'上市公司公告信息，敬请查收附件，谢谢！' 
    
    cf=ConfigParser.ConfigParser()
    cf.read('passwd.ini')  #读配置文件（ini、conf）返回结果是列表
    username = cf.get('passwdini','username') #获取邮箱账号       
    password = cf.get('passwdini','password') #获取邮箱密码     
    senderMail = cf.get('passwdini','senderMail') #获取发件箱
    cclist = []
    maillist= ['yangchg@scfund.com.cn','ycg860102@163.com']
    filelist = [filepath]
    mail2.send_mail(senderMail, maillist,subject,text,filelist,cclist,'mail.scfund.com.cn', username, password)        #发送


if __name__ == '__main__':
    """
    #SecNodeType=5 , 业绩预告
    #SecNodeType=6 , 业绩快报
    #SecNodeType=1 , 定期预告
    Time=YYYY-MM-DD 日期
    """
    now = datetime.datetime.now()
    #取公告日为明天的上市公司
    tommrow =now + datetime.timedelta(days = 1)
    Time=tommrow.strftime('%Y-%m-%d') 
    #Time = '2018-04-13'
    SecNodeTypes = dict({1:u"定期报告",5:u"业绩预告",6:u"业绩快报"} ) 
    #SecNodeTypes = dict({1:u"定期报告",} ) 
    tinyedDF = pd.DataFrame()
    
    #依次爬取不同类型的公告数据
    for SecNodeType,SecNodeName in SecNodeTypes.items():
        #由于不知道当天有多少页数据，所以默认取50页，当没有数据时会跳出循环
        for PageIndex in range(50) :
            PageIndex=PageIndex+1 
            url = "http://data.eastmoney.com/notices/getdata.ashx?StockCode=&FirstNodeType=1&CodeType=1&PageIndex="+str(PageIndex)+"&PageSize=50&SecNodeType="+str(SecNodeType)+"&Time="+Time
            #crawl(url)
            resp = requests.get(url, headers=headers) 
            
            page = resp.content
            
            pattern = "^var  = (.*?);$" 
            res = re.search(pattern, page)
            resData = res.groups(1) 
            jsonData = json.loads(resData[0],encoding="GBK") 
            
            for i in range(len(jsonData["data"])):
                tinyedData = dict()
                tinyedData[u"证券代码"]= jsonData["data"][i]["ANN_RELCODES"][0]["SECURITYCODE"]
                
                tinyedData[u"公告名称"]= jsonData["data"][i]["NOTICETITLE"]
                tinyedData[u"公告日期"]= jsonData["data"][i]["NOTICEDATE"][:10]
                tinyedData[u"公告类型"]= jsonData["data"][i]["ANN_RELCOLUMNS"][0]["COLUMNNAME"]
                tinyedData[u"链接地址"]= jsonData["data"][i]["Url"]
                tinyedDF = tinyedDF.append(pd.DataFrame(tinyedData,index=[0]))
            if  len(jsonData["data"]) <50 :
                break 
    #公告保存地址        
    filepath = u"D:\\量化程序\\公告\\"+Time+u"公司公告.xlsx" 
    if len(tinyedDF) >0 :
        #调用天软模块，取所有股票的申万行业名称
        TSLPy2.RemoteCallFunc('getSWindustry2',[],{}) 
        #读取天软导出的申万行业名称
        swhyfl = pd.read_excel(u"D:\\量化程序\\公告\\申万行业分类.xlsx",converters = {u'证券代码':str})
        #关联行业名称
        mergedtinyedDF = pd.merge(tinyedDF,swhyfl,how='left',left_on=[u'证券代码'],right_on=[u'证券代码'])
        
        #设置excle 各列的顺序
        mergedtinyedDF=mergedtinyedDF[[u"公告日期",u"证券代码",u"证券名称",u"申万一级名称",u"公告名称",u"公告类型",u"链接地址"]]
        #对结果按照申万一级行业和证券代码排序
        mergedtinyedDF=mergedtinyedDF.sort_values(by=[u"申万一级名称",u"证券代码"])
        #设置索引从1开始计数
        mergedtinyedDF.index = range(1,len(mergedtinyedDF) + 1) 
        #保存到excel
        mergedtinyedDF.to_excel(filepath)
        #将excel发送邮件
        sendMail(filepath)
        
        
    #NOTICETITLE1 = jsonpath.jsonpath(jsonData,'$.data.1.NOTICETITLE')
    
    #pattern2 = "(.*?)NOTICEDATE\":\"(?P<a>.*?)\","
    #res = re.match(pattern2,page)
    #resdict = res.groupdict()
    
    
    #resData = res.groups(1) 
    #jsonData = json.loads(resData) 
    