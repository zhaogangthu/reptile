import sys
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import datetime
import mysql.connector
import re

import sys
import socks
from telethon import TelegramClient, sync
import os


def process_telegram_list():
    #######################
    url_list2=[]
    try:
        conn = mysql.connector.connect(host='***m', user='***', passwd='***', db='***')
    except:
        print('aaaa')
        sys.exit()
    cursor = conn.cursor()

    # SQL 查询语句
    search_sql ='select * from h_hot'
    try:
        # 执行SQL语句
        cursor.execute(search_sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            if row[2]!=None and row[2]!='':
                token_cid = row[1]
                token_url = row[2]

                # 打印结果
                #print(token_id, token_name, token_symbol, token_github_master)
                url_list2.append([token_cid, token_url])
    except:
        print("Error: unable to fecth data")

    # 关闭数据库连接
    cursor.close()
    conn.close()
    ################

    url_list_mysql=[]

    today=str(datetime.date.today().strftime('%Y%m%d'))

    count=0


    api_id = 123456  # 用户api_id
    api_hash = '***'  # 用户 api_hash
    phone_number = '+123456'  # 用户号码

    # client = TelegramClient('session_id',
    #                         api_id=api_id, api_hash=api_hash,
    #                         # proxy=(socks.SOCKS5, 'localhost', 61800)
    #                         proxy=(socks.SOCKS5, 'localhost', 61800)
    #                         )
    client = TelegramClient('session_id', api_id, api_hash)
    client.session.report_errors = False
    client.start()
    client.connect()
    for i in range(len(url_list2)):
    #for i in range(3):
        try:
            channel_str = url_list2[i][1]
            if 'https://t.me/' in channel_str and 'join' not in channel_str:
                channel = client.get_entity(channel_str)  # 'https://t.me/StratisPlatform'
                print(i,len(url_list2),url_list2[i][1])
                participants = client.get_participants(channel)
                cangku2={}
                cangku2['personNum']=str(len(participants))
                cangku2['updateTime'] = today
                cangku2['cid'] = str(url_list2[i][0])
                cangku2['telegramUrl'] = str(url_list2[i][1])
                url_list_mysql.append(cangku2)
                count=count+1
        except:
            print('error!',url_list2[i])
    print(str(count)+'个数据爬取完成')

    return url_list_mysql,count


now_time1=datetime.datetime.now()
print (now_time1)
url_list_mysql,reptile_count=process_telegram_list()
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
        insert_sql='insert into h_reptile_telegram(cid, telegramUrl, ' \
                    'personNum, updateTime)' \
                    ' values('+url_list_mysql[i]['cid']+',\"'+url_list_mysql[i]['telegramUrl']+'\",'+\
                   url_list_mysql[i]['personNum']+','+url_list_mysql[i]['updateTime']+')'
        print(insert_sql)
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