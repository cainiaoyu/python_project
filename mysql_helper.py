#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 处理数据库的类


import MySQLdb
import ConfigParser


class MySQLDBHelper:
    # 获取数据库连接
    def __init__(self):
        try:
            mysql_config = ConfigParser.RawConfigParser()
            mysql_config.read('app_mysql_config.cfg')
            mysql_host = mysql_config.get("mysql", "host")
            mysql_user = mysql_config.get("mysql", "user")
            mysql_passwd = mysql_config.get("mysql", "passwd")
            mysql_db = mysql_config.get("mysql", "db")
            mysql_port = mysql_config.getint("mysql", "port")
            mysql_charset = mysql_config.get("mysql", "charset")
            conn = MySQLdb.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd,
                                   db=mysql_db, port=mysql_port, charset=mysql_charset)
            self.cur = conn.cursor(MySQLdb.cursors.DictCursor)
        except MySQLdb.Error, e:
            print "db Error:%s" % e
            # 查询方法，使用con.cursor(MySQLdb.cursors.DictCursor),返回结果为字典

    def select(self, sql):
        try:
            self.cur.execute(sql)
            fc = self.cur.fetchall()
            return fc
        except MySQLdb.Error, e:
            print "db Error:%s" % e

    def close_connect(self):
        self.cur.close()
        self.conn.close()

"""    def updateByParam(self, sql, params):
        try:
            con = self.getCon()
            cur = con.cursor()
            count = cur.execute(sql, params)
            con.commit()
            return count
        except MySQLdb.Error, e:
            con.rollback()
            print "Mysqldb Error:%s" % e
        finally:
            cur.close()
            con.close()
            # 不带参数的更新方法

    def update(self, sql):
        try:
            con = self.getCon()
            cur = con.cursor()
            count = cur.execute(sql)
            con.commit()
            return count
        except MySQLdb.Error, e:
            con.rollback()
            print "Mysqldb Error:%s" % e
        finally:
            cur.close()
            con.close()
"""

