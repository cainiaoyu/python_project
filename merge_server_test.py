#!/bin/env python
# -*- coding: utf-8 -*-
"""合服工具
   新代码按照PEP8规范


"""''
import MySQLdb
import yaml
import os

YAML_FILENAME = "merge_config"   # 配置合服服务器ID文件名，一般和merge_server.py 脚本放在一起
LOGIN_DB_IP = "192.168.199.102"  # 登陆服务器数据库所在地址， 用于根据ID查询服务器所在的IP和端口信息
LOGIN_DB_PSW = "123321"  # 登陆服务器密码
LOGIN_DB_USER = "yx"  # 登陆服务器用户名
LOGIN_DB_NAME = "dragonlogindata"  # 登陆服务器数据库名
LOGIN_DB_PORT = 3306  # 登陆服务器端口
DB_CHARSET = "utf8"  # 设置默认数据库编码
DTL_GAME_BASE = "/data/ywygame_dtl/"  # 大屠龙游戏服务器安装路径
TZ_GAME_BASE = "/data/ywygame/"  # 天尊服务器安装路径
TZ_LEGEND = 81  # 天尊传奇区id, 因为天尊传奇区在服务区安装路径，游戏数据库名区别于其他游戏服务器


def tz_or_dtl(server_id):
    """判断是天尊服务器还是大屠龙服务器
    :param server_id:
    :return: string
    """
    if server_id < 10000:
        return "tz"
    else:
        return "dtl"


def is_legend_server(server_id):
    """判断是否为传奇服务器（包括合服后为传奇区），因为传奇服务器的数据库名字和在linux下存放的路径名比较特殊
    :param server_id:
    :return: boole
    """
    # 根据服务器ID查出来的IP地址和端口都是和现在的传奇区服务器地址、端口一样的话， 就属于传奇区
    if tz_or_dtl(server_id) == "tz":
        if (game_server_port(server_id) == game_server_port(TZ_LEGEND)) and (game_server_address(server_id) == game_server_address(TZ_LEGEND)):
            return True
        else:
            return False
    else:
        return False


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


def game_server_port(server_id):
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
            return int(res[0])
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def game_server_name(server_id):
    if is_legend_server(server_id):
        return "gameserver"
    else:
        return "gameserver_" + str(server_id)


def game_server_dir(server_id):
    if tz_or_dtl(server_id) == "tz":
        return os.path.join(TZ_GAME_BASE, game_server_name(server_id))
    else:
        return os.path.join(DTL_GAME_BASE, game_server_name(server_id))


def game_server_address(server_id):
    """游戏服务器的地址

    :return: string
    """
    sql = "SELECT s_ip FROM server where s_id = %d" % server_id
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
            return res[0].encode("utf8")
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def shutdown_game(ip, port):
    pass


if __name__ == "__main__":
    print game_server_dir(10061)
