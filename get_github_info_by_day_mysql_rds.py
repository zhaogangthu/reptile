import sys
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import datetime
import mysql.connector

#from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTP

import pandas as pd
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行


# 自动发送邮件
def auto_send_email(to_address, subject, content, from_address='***@qq.com', if_add_time=True):
    """
    :param to_address: 收件人地址
    :param subject: 邮件主题
    :param content: 邮件正文
    :param from_address: 发件人地址
    :return:
    使用foxmail发送邮件的程序
    """
    # try:

    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    username = from_address
    password = '***'

    server = SMTP('smtp.qq.com', port=587)
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()

    print('邮件发送成功')
    # except Exception as err:
    #     print('邮件发送失败', err)

def getHtml(url,values):
    user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    headers = {'User-Agent':user_agent}
    data = urllib.parse.urlencode(values)
    response_result = urllib.request.urlopen(url+'?'+data).read()
    html = response_result.decode('utf-8')
    return html

def requestCnblogs(url):
    value= {
         'CategoryId':808,
         'CategoryType' : 'SiteHome',
         'ItemListActionName' :'PostList',
         'PageIndex' : 0,
         'ParentCategoryId' : 0,
        'TotalPostCount' : 4000
    }
    result = getHtml(url,value)
    return result

def process_github_list():
    #######################
    url_list2=[]
    try:
        conn = mysql.connector.connect(host='***', user='***', passwd='***', db='***')
    except:
        print('aaaa')
        sys.exit()
    cursor = conn.cursor()

    # SQL 查询语句
    search_sql ='select * from h_currency'
    try:
        # 执行SQL语句
        cursor.execute(search_sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            token_id = row[0]
            token_name = row[1]
            token_symbol = row[2]
            token_github_master = row[42]
            # 打印结果
            #print(token_id, token_name, token_symbol, token_github_master)
            url_list2.append([token_id, token_name, token_symbol, token_github_master])
    except:
        print("Error: unable to fecth data")

    # 关闭数据库连接
    cursor.close()
    conn.close()
    ################

    url_list_mysql=[]

    today=str(datetime.date.today().strftime('%Y%m%d'))

    count=0
    for i in range(len(url_list2)):
    #for i in range(3):
        try:
            #print(url_list2[i])
            cnblogs = requestCnblogs(url_list2[i][3])
            soup = BeautifulSoup(cnblogs, 'html.parser')
            cangku=analyze_process_github_list(soup)

            if len(cangku)==6:
                cangku['githubMaster']=url_list2[i][3]
                cangku['updateTime']=today
                cangku['cid']=str(url_list2[i][0])
                url_list_mysql.append(cangku)
                count=count+1
                #print(url_list2[i])
        except:
            if url_list2[i][3]!=None:
                auto_send_email(to_address='***', subject='github url error!', content='id: '+str(url_list2[i][0])+'\ncoin_name: '+url_list2[i][1],from_address='***@qq.com')
            print(url_list2[i])
    print(str(count)+'个数据爬取完成')

    return url_list_mysql,count

def analyze_process_github_list(item):
    cangku={}


    div_list = item.find_all('ul',attrs={'class': 'pagehead-actions'}, limit=1)
    if len(div_list)==1:
        li=div_list[0].find_all('li', limit=3)
        cangku['watch']=(li[0].find_all('a', limit=2)[1].string.strip().replace(',',''))
        cangku['star'] = (li[1].find_all('a', limit=2)[1].string.strip().replace(',',''))
        cangku['fork'] = (li[2].find_all('a', limit=2)[1].string.strip().replace(',',''))

        div_list = item.find_all('ul', attrs={'class': 'numbers-summary'}, limit=1)
        if len(div_list)==1:
            li = div_list[0].find_all('li', limit=4)
            cangku['commits'] = (li[0].find_all('span',attrs={'class': 'num text-emphasized'}, limit=1)[0].string.strip().replace(',',''))
            cangku['releases'] = (li[2].find_all('span',attrs={'class': 'num text-emphasized'}, limit=1)[0].string.strip().replace(',',''))
            if li[3].find_all('span', attrs={'class': 'num text-emphasized'},limit=1)[0].string!=None:
                cangku['contributors'] = (li[3].find_all('span', attrs={'class': 'num text-emphasized'},limit=1)[0].string.strip().replace(',',''))
    return cangku




now_time1=datetime.datetime.now()
print (now_time1)
url_list_mysql,reptile_count=process_github_list()
now_time=datetime.datetime.now()

try:
    conn = mysql.connector.connect(host='***', user='***', passwd='***', db='***')
except:
    print(sys.stderr)
    sys.exit()
cursor = conn.cursor()
count=0
for i in range(len(url_list_mysql)):
#for i in range(2):
    try:
        insert_sql='insert into h_reptile_github( watch, star, ' \
                    'fork, commits, releases, contributors, cid, updateTime,githubMaster)' \
                    'values('+url_list_mysql[i]['watch']+','+url_list_mysql[i]['star']+','+\
                   url_list_mysql[i]['fork']+','+url_list_mysql[i]['commits']+','\
                   +url_list_mysql[i]['releases']+','+url_list_mysql[i]['contributors']+','\
                   +url_list_mysql[i]['cid']+','+\
                   url_list_mysql[i]['updateTime']+',\"'+url_list_mysql[i]['githubMaster']+'")'
        #print(insert_sql)
        cursor.execute(insert_sql)
        count=count+1
    except:
        print(insert_sql)

conn.commit()

now_time=datetime.datetime.now()
print(str(reptile_count)+'个网页爬取成功！')
print(str(count)+'个数据存入数据库！')
print ('开始时间：',now_time1)
print('完成时间：',now_time)
print ('共计用时：',now_time-now_time1)