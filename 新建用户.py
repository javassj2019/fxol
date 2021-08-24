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
        cur.execute('insert into User(UserID,UserPassword,Mark) VALUES (%s,%s,%s)', (userAccount, userPassword, 0))
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