#mail.py
#coding: utf-8 
import sys, smtplib, MimeWriter, base64, StringIO, os, string, time

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_from, send_to, subject, text, files=[], send_cc = None,
              server="localhost", user = None, password = None):
    assert type(send_to)==list
    assert type(files)==list
    assert type(send_cc)==list

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Cc'] = COMMASPACE.join(send_cc)
    #msg['Subject'] = unicode(subject,"gbk")
    msg['Subject'] = subject 
    
    msg.attach( MIMEText(text,'html','utf8') )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        ufile = file
        part.set_payload( open(ufile,"rb").read())
        Encoders.encode_base64(part)
        basename =  os.path.basename(ufile)
 
        part.add_header("Content-Disposition","attachment",filename=basename.encode('utf8')) 
              
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp = smtplib.SMTP()
    smtp.connect(server)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
##    smtp.set_debuglevel(1)
    smtp.login(user,password)
    
    smtp.sendmail(send_from, send_to, msg.as_string())
    print(u'成功');
    smtp.close()


##filedata = time.strftime("%Y%m%d", time.localtime())
##
##text = '联系人手册,请查收，谢谢!'
##maillist = ['yangchg@scfund.com.cn','ycg860102@163.com']
##
##cclist = []
##
##file1 = 'E:\联系人手册%s.xls' % (filedata)
##
##print file1
##
##filelist = ['E:\联系人手册%s.xls' % (filedata)]
##
##send_mail('yangchg@scfund.com.cn', maillist,'联系人手册',
##                text,filelist,cclist,'mail.scfund.com.cn', 'yangchg', '')
