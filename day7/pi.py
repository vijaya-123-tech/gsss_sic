import pymysql
connection=pymysql.connect(host='localhost',
                           user='root',
                           password='root',
                           database='viju_db')
'''if connection:
    print("db is connected")
else:
    print("db is not connected ")'''
cursor=connection.cursor()
'''cursor.execute("create database employee")'''
'''cursor.execute("show databases")'''
cursor.execute("create table manager (name varchar(20),salary float(40),id int primary)")


for x in cursor:
    print(x)