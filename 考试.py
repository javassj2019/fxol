import requests
import json
import pymysql
import re
import datetime
import urllib
# -*- coding:utf-8 -*-
# 连接数据库并获取账户密码信息
conn = pymysql.connect(host='cdb-kce5k8kq.bj.tencentcdb.com', user='root', passwd='a159753A!', port=10264,
                       charset='utf8', db='fxol')
cur = conn.cursor(pymysql.cursors.DictCursor)  # 生成游标


# # 录入新用户
# def Typeuserid():
#     print('请输入用户名：')
#     userAccount = input()
#     print('请输入密码：')
#     userPassword = input()
#     # 用户查重
#     checkuid = cur.execute('select UserID from User where UserID = (%s)', userAccount)
#     print(checkuid)
#     if checkuid == 0:
#         cur.execute('insert into User(UserID,UserPassword,TDpoint) VALUES (%s,%s,%s)', (userAccount, userPassword, 10))
#         conn.commit()
#         print('用户添加完成')
#     else:
#         print('用户已存在，无需再次添加')
#
#
# print('需要添加新用户吗？Yes')
# checktype = input()
# if checktype == 'Y':
#     i = 0
#     while i <= 100:
#         Typeuserid()
#         i = i + 1

###基础数据
http = 'http://'
host = 'mobile.faxuan.net'
loginurl = '/bss/service/userService!doUserLogin.do?'
getdetailurl = '/useris/service/getdetail?userAccount='
studyurl = '/sss/service/coursewareService!commitStudy.do?domainCode='
code = '&code=2f56fe3477f774c4ece2b926070b6d0a'
headers = {}
headers['If-Modified-Since'] = 'Tue, 1 Jul 2021 01:33:10 GMT+00:00'
headers['User-Agent'] = 'Dalvik/2.1.0 (Linux; U; Android 7.1.1; OPPO R9s Build/NMF26F)'
headers['Host'] = 'mobile.faxuan.net'
headers['Accept-Encoding'] = 'gizp,deflate'
headers['Connection'] = 'keep-alive'
headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
answerjson = '\[(.*)\]'

####比较最后更新时间并写数据库
today = str(datetime.date.today())
###开始登陆过程
s = 0
l = cur.execute('select UserID,UserPassword from User where Mark = (%s)', (3))

while s <= l:
    cur.execute('select UserID,UserPassword from User where Mark = (%s)', (3))
    tt1 = cur.fetchone()
    print(tt1)
    userAccount = tt1['UserID']
    userPassword = tt1['UserPassword']
    # 登陆并获取参数
    tt = requests.get(http + host + loginurl + 'userAccount=' + userAccount + '&userPassword=' + userPassword + code,
                      headers=headers)
    dd = json.loads(tt.text)
    sid = dd['data']['sid']
    # username = dd['data']['userName']
    # 获取学员基础信息
    t2 = requests.get(http + host + getdetailurl + userAccount + '&ssid=' + sid, headers=headers)
    t2.encoding = 'utf8'
    d2 = json.loads(t2.text)
    lenth = len(d2)
    dict1 = {}
    i = 0
    while i <= lenth-1:
        dict1[d2[i]] = d2[i + 1]
        i = i + 2
    TDpoint = dict1['todaytpoint']
    domainCode = dict1['domainCode']
    Tpoint = dict1['tpoint']
    username = dict1['userName']
    print(username)

    # 开始考试
    examid = str(2440)
    paperid = str(4932)
    series = str(430)
    t4 = requests.get(
        http + host + '/ess/service/getpaper?paperId='+paperid+'&series='+series+'_answer&version=2.5.5&userAccount' + userAccount,
        headers=headers)
    # print(t4.text)
    t4answer = re.findall(answerjson, str(t4.content))[0]  # 此处返回text会因为返回有非json的数据不能读取

    t4answer = t4answer.replace(',"score":"1.0",', ',')
    t4answer = t4answer.replace(',"score":"2.0",', ',')
    t4answer = t4answer.replace(',"score":"3.0",', ',')
    t4answer = t4answer.replace('questionId":"', 'questionId":')
    t4answer = t4answer.replace('","answerNo', ',"answerNo')
    t4answer = t4answer.replace('},{', '}{')
    t4answer = t4answer.replace('ABCD', 'A,B,C,D')
    t4answer = t4answer.replace('ABC', 'A,B,C')
    t4answer = t4answer.replace('ABD', 'A,B,D')
    t4answer = t4answer.replace('ACD', 'A,C,D')
    t4answer = t4answer.replace('BCD', 'B,C,D')
    t4answer = t4answer.replace('AC', 'A,C')
    t4answer = t4answer.replace('AD', 'A,D')
    t4answer = t4answer.replace('BC', 'B,C')
    t4answer = t4answer.replace('BD', 'B,D')
    t4answer = t4answer.replace('CD', 'C,D')
    answer = t4answer
    data = {
        'series': series,
        'examId': examid,
        'paperId': paperid,
        'userAccount': userAccount,
        'domainCode': domainCode,
        'myExamAnswer': '[' + answer + ']'
    }
    t6 = requests.post(
        http + host + '/ess/service/myexam/myExamAo!doCommitExam.do',
        headers=headers,
        data=data
    )
    # print(t6.text)
    cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (4, userAccount))
    conn.commit()
    print("学习过程结束")
    ##########这里还差学习执行过程
