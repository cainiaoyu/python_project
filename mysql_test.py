#!/bin/env python
# -*- coding: utf-8 -*-


import MySQLdb


if __name__ == "__main__":
    cnn = MySQLdb.connect(user="yx", passwd="123321", host="192.168.199.102",
                          charset="utf8", db="test")
    sql = "select * from info"
    info_id = 1
    cur = cnn.cursor()
    res = cur.execute(sql, (info_id,))
    print res.rowcount
