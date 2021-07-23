import requests
import json
import pymysql
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
###执行一次初始化数据刷新
s = 0
l = cur.execute('select UserID,UserPassword from User where Mark = (%s)', (0))

while s <= l:
    cur.execute('select UserID,UserPassword from User where Mark = (%s)', (0))
    tt1 = cur.fetchone()
    try:
        userAccount = tt1['UserID']
        userPassword = tt1['UserPassword']
        # 登陆并获取参数
        tt = requests.get(
            http + host + loginurl + 'userAccount=' + userAccount + '&userPassword=' + userPassword + code,
            headers=headers)
        dd = json.loads(tt.text)
        sid = dd['data']['sid']
        # username = dd['data']['userName']
        # 获取学员基础信息
        t2 = requests.get(http + host + getdetailurl + userAccount + '&ssid=' + sid, headers=headers)
        cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (1, userAccount))
        conn.commit()
    except TypeError:
        print('全部数据已读取，开始进入数据刷新阶段。。。。。。')
        break




###开始登陆过程
s = 0
l = cur.execute('select UserID,UserPassword from User where Mark = (%s)', (1))

while s <= l:
    cur.execute('select UserID,UserPassword from User where Mark = (%s)', (1))
    tt1 = cur.fetchone()
    try:
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
        print(username+'今日积分为：'+TDpoint+'，全部积分为：'+Tpoint)
        #写入数据库
        cur.execute('UPDATE User SET Name = (%s) WHERE UserID = (%s)', (username, userAccount))
        cur.execute('UPDATE User SET Tpoint = (%s) WHERE UserID = (%s)', (Tpoint, userAccount))
        cur.execute('UPDATE User SET TDpoint = (%s) WHERE UserID = (%s)', (TDpoint, userAccount))
        cur.execute('UPDATE User SET Updata = (%s) WHERE UserID = (%s)', (today, userAccount))
        if int (Tpoint) > 2400:
            cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (3, userAccount))
        else:
            if int(TDpoint) < 150:
                cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (0, userAccount))
            else:
                cur.execute('UPDATE User SET Mark = (%s) WHERE UserID = (%s)', (2, userAccount))
        conn.commit()
        print("积分刷新结束")
    except TypeError:
        print('未找到符合条件的数据，请检查数据库')
        break
