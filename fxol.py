import requests
import json
import pymysql
import re
import datetime

# -*- coding:utf-8 -*-
# 连接数据库并获取账户密码信息
conn = pymysql.connect(host='cdb-kce5k8kq.bj.tencentcdb.com', user='root', passwd='a159753A!', port=10264,
                       charset='utf8', db='fxol')
cur = conn.cursor(pymysql.cursors.DictCursor)  # 生成游标


# 录入新用户
def Typeuserid():
    print('请输入用户名：')
    userAccount = input()
    print('请输入密码：')
    userPassword = input()
    # 用户查重
    checkuid = cur.execute('select UserID from User where UserID = (%s)', userAccount)
    print(checkuid)
    if checkuid == 0:
        cur.execute('insert into User(UserID,UserPassword,TDpoint) VALUES (%s,%s,%s)', (userAccount, userPassword, 10))
        conn.commit()
        print('用户添加完成')
    else:
        print('用户已存在，无需再次添加')


print('需要添加新用户吗？Yes')
checktype = input()
if checktype == 'Y':
    i = 0
    while i <= 100:
        Typeuserid()
        i = i + 1

###基础数据
http = 'http://'
host = 'mobile.faxuan.net'
loginurl = '/bss/service/userService!doUserLogin.do?'
getdetailurl = '/useris/service/getdetail?userAccount='
studyurl = '/sss/service/coursewareService!commitStudy.do?domainCode='
code = '&code=2f56fe3477f774c4ece2b926070b6d0a'
headers = {}
headers['If-Modified-Since'] = 'Tue, 25 Dec 2018 01:33:10 GMT+00:00'
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
l = cur.execute('select UserID,UserPassword from User where Mark < (%s) AND TDpoint < (%s)', (3,150))

while s <= l:
    cur.execute('select UserID,UserPassword from User where Mark < (%s) AND TDpoint < (%s)', (3,150))
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
    # 开始学习,下一行是学习时间提交的
    t3 = requests.get(
        http + host + studyurl + domainCode + '&userAccount=' + userAccount + '&stime=241&ssid=' + sid + '&validate=&type=2',
        headers=headers)
    # 开始自动做练习题
    t4 = requests.get(
        http + host + '/ess/service/getpaper?paperId=2790&series=21_answer&version=2.5.5&userAccount' + userAccount,
        headers=headers)
    t4answer = re.findall(answerjson, str(t4.content))[0]  # 此处返回text会因为返回有非json的数据不能读取
    # print(type(t4answer),t4answer)
    t5 = json.loads('[' + t4answer + ']')
    # print(t5[0])
    k = 0
    answer = ''
    while k <= 49:
        answer = answer + '{%22questionId%22:' + t5[k]['questionId'] + ',%22answerNo%22:%22' + t5[k][
            'answerNo'] + '%22}'
        k = k + 1
    t6 = requests.get(
        http + host + '/sss/service/coursewareService!commitExercises.do?domainCode=' + domainCode + '&userAccount=' + userAccount + '&paperId=2790&series=21&myExamAnswer=[' + answer + ']&ssid=' + sid + '&validate=&type=2',
        headers=headers)
    tkk = requests.post('http://mobile.faxuan.net/ess/service/myexam/myExamAo!doCommitExam.do',headers=headers,data='domainCode='+domainCode+'&series=43&userAccount='+userAccount+'&examId=2034&myExamAnswer=%5b%7b%22questionId%22%3a%22566846%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566833%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566851%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566840%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566828%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566842%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566830%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566838%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566836%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566829%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566834%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566854%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566843%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566848%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566835%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566827%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566832%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566831%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566852%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566844%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566826%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566847%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566839%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566837%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566841%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566853%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566850%22%22answerNo%22%3a%22A%22%7d%7b%22questionId%22%3a%22566855%22%22answerNo%22%3a%22B%22%7d%7b%22questionId%22%3a%22566845%22%22answerNo%22%3a%22D%22%7d%7b%22questionId%22%3a%22566849%22%22answerNo%22%3a%22C%22%7d%7b%22questionId%22%3a%22566934%22%22answerNo%22%3a%22ABC%22%7d%7b%22questionId%22%3a%22566916%22%22answerNo%22%3a%22ABD%22%7d%7b%22questionId%22%3a%22566925%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566921%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566922%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566928%22%22answerNo%22%3a%22BC%22%7d%7b%22questionId%22%3a%22566920%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566930%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566918%22%22answerNo%22%3a%22AB%22%7d%7b%22questionId%22%3a%22566924%22%22answerNo%22%3a%22AB%22%7d%7b%22questionId%22%3a%22566919%22%22answerNo%22%3a%22ABC%22%7d%7b%22questionId%22%3a%22566931%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566923%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566933%22%22answerNo%22%3a%22BCD%22%7d%7b%22questionId%22%3a%22566932%22%22answerNo%22%3a%22ABC%22%7d%7b%22questionId%22%3a%22566927%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566926%22%22answerNo%22%3a%22ABC%22%7d%7b%22questionId%22%3a%22566935%22%22answerNo%22%3a%22BC%22%7d%7b%22questionId%22%3a%22566917%22%22answerNo%22%3a%22ABC%22%7d%7b%22questionId%22%3a%22566929%22%22answerNo%22%3a%22ABCD%22%7d%7b%22questionId%22%3a%22566977%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566970%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566968%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566974%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566978%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566971%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566964%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566975%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566976%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566969%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566966%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566967%22%22answerNo%22%3a%220%22%7d%7b%22questionId%22%3a%22566973%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566965%22%22answerNo%22%3a%221%22%7d%7b%22questionId%22%3a%22566972%22%22answerNo%22%3a%221%22%7d%5d&paperId=4409&')
    #print(tkk.text)
    cur.execute('UPDATE User SET Name = (%s) WHERE UserID = (%s)', (username, userAccount))
    cur.execute('UPDATE User SET Tpoint = (%s) WHERE UserID = (%s)', (Tpoint, userAccount))
    cur.execute('UPDATE User SET TDpoint = (%s) WHERE UserID = (%s)', (TDpoint, userAccount))
    cur.execute('UPDATE User SET Updata = (%s) WHERE UserID = (%s)', (today, userAccount))
    cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (2, userAccount))
    conn.commit()
    print("学习过程结束")
    ##########这里还差学习执行过程
