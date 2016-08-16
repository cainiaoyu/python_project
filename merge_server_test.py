#!/bin/env python
# -*- coding: utf-8 -*-
"""合服工具
   新代码按照PEP8规范


"""''
import MySQLdb
import yaml

YAML_FILENAME = "merge_config"   # 配置合服服务器ID文件名，一般和merge_server.py 脚本放在一起
LOGIN_DB_IP = "192.168.199.102"  # 登陆服务器数据库所在地址， 用于根据ID查询服务器所在的IP和端口信息
LOGIN_DB_PSW = "123321"  # 登陆服务器密码
LOGIN_DB_USER = "yx"  # 登陆服务器用户名
LOGIN_DB_NAME = "dragonlogindata"  # 登陆服务器数据库名
LOGIN_DB_PORT = 3306  # 登陆服务器端口
DB_CHARSET = "utf8"  # 设置默认数据库编码


def destination_server():
    """返回目标服务器ID
    :return: int
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"][0]


def original_server():
    """ 返回源服务器ID列表
    :return: list
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"][1:]


def all_server_list():
    """返回所有服务器ID

    :return: list
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"]


def game_data_name(server_list):
    """返回游戏数据库名

    :return: string list
    """
    name_list = []
    for id_ in server_list:
        name_list.append("dragongamedata_" + str(id_))
    return name_list


def game_log_name(server_list):
    """返回游戏日志数据库名

    :return: string list
    """
    name_list = []
    for id_ in server_list:
        name_list.append("dragongamelog_" + str(id_))
    return name_list


def game_port(server_id):
    """游戏服务器的端口

    :return: int
    """
    # sql = "SELECT s_port FROM server WHERE s_id = %d" % (server_id)
    sql = "SELECT s_port FROM server where s_id = %d" % server_id
    try:
        conn = MySQLdb.connect(user=LOGIN_DB_USER, passwd=LOGIN_DB_PSW, host=LOGIN_DB_IP, port=LOGIN_DB_PORT,
                               charset=DB_CHARSET, db=LOGIN_DB_NAME)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res is None:
            print "没有找到相关记录，请检查服务器id: %d 是否正确" % server_id
        else:
            return res[0]
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def game_address():
    """游戏服务器的地址

    :return: string
    """
    pass

if __name__ == "__main__":
    print destination_server()
    print original_server()
    print all_server_list()
    print game_data_name(all_server_list())
    print game_log_name(all_server_list())
    print game_port(10061)

