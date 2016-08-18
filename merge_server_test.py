#!/bin/env python
# -*- coding: utf-8 -*-
"""合服工具
   新代码按照PEP8规范


"""''
import MySQLdb
import yaml
import os
import paramiko
import socket

from paramiko import SSHException

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
RAS_KEY_FILE = "/root/.ssh/id_rsa"


def tz_or_dtl(server_id):
    """判断是天尊服务器还是大屠龙服务器
    :param int server_id: 游戏服务器id
    :return: 字符串"tz"或者"dtl"表明天尊还是大屠龙服务器
    """
    if server_id < 10000:
        return "tz"
    else:
        return "dtl"


def is_legend_server(server_id):
    """判断是否为传奇服务器（包括合服后为传奇区），因为传奇服务器的数据库名字和在linux下存放的路径名比较特殊
    :param int server_id: 游戏服务器id
    :return: 是否为传奇区服务器
    """
    # 根据服务器ID查出来的IP地址和端口都是和现在的传奇区服务器地址、端口一样的话， 就属于传奇区
    if tz_or_dtl(server_id) == "tz":
        if (game_server_port(server_id) == game_server_port(TZ_LEGEND)) and \
                (game_server_address(server_id) == game_server_address(TZ_LEGEND)):
            return True
        else:
            return False
    else:
        return False


def destination_server():
    """根据merger_config配置文件里的server_id
    生成目标服务器即合服的最终服务器
    :return: 返回目标服务器id
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"][0]


def original_server():
    """ 根据merger_config配置文件里的server_id
    生成源服务器id列表，可能是多个
    :return: 返回源服务器ID列表
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"][1:]


def all_server_list():
    """根据merger_config配置文件里的server_id
     返回所有配置的服务器id
    :return: 返回所有服务器ID
    """
    fd = open(YAML_FILENAME)
    server_id = yaml.load(fd)
    fd.close()
    return server_id["server_list"]


def game_data_name(server_list):
    """根据服务器列表生成游戏服务器data数据库名字
    :param list server_list :
    :return: 返回游戏数据库名
    """
    name_list = []
    for id_ in server_list:
        name_list.append("dragongamedata_" + str(id_))
    return name_list


def game_log_name(server_list):
    """根据服务器列表生成游戏服务器log数据库名字
    :param list server_list: 游戏服务器列表
    :return: 返回游戏日志数据库名
    """
    name_list = []
    for id_ in server_list:
        name_list.append("dragongamelog_" + str(id_))
    return name_list


def game_server_port(server_id):
    """根据游戏服务器id返回游戏服务器所在物理服务器的端口
    :param int server_id: 游戏服务器id
    :return: 游戏服务器的端口
    """
    # sql = "SELECT s_port FROM server WHERE s_id = %d" % (server_id)
    sql = "SELECT s_port FROM server where s_id = %d" % server_id
    try:
        conn = MySQLdb.connect(user=LOGIN_DB_USER, passwd=LOGIN_DB_PSW,
                               host=LOGIN_DB_IP, port=LOGIN_DB_PORT,
                               charset=DB_CHARSET, db=LOGIN_DB_NAME)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res is None:
            print "没有找到相关记录，请检查服务器id: %d 是否正确" % server_id
            exit(100)
        else:
            return int(res[0])
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def game_server_name(server_id):
    """根据游戏服务器id规定游戏服务器在物理服务器上的文件夹名字
    传奇区名字特殊
    :param int server_id:
    :return: 游戏服务器id所在物理服务器文件夹名
    """
    if is_legend_server(server_id):  # 判断是否为传奇区
        return "gameserver"
    else:
        return "gameserver_" + str(server_id)


def game_server_dir(server_id):
    if tz_or_dtl(server_id) == "tz":
        return os.path.join(TZ_GAME_BASE, game_server_name(server_id))
    else:
        return os.path.join(DTL_GAME_BASE, game_server_name(server_id))


def game_server_address(server_id):
    """根据游戏服务器id返回其所在的物理服务器IP地址

    :return: 指定游戏服务器id的物理服务器地址
    """
    sql = "SELECT s_ip FROM server where s_id = %d" % server_id
    try:
        conn = MySQLdb.connect(user=LOGIN_DB_USER, passwd=LOGIN_DB_PSW,
                               host=LOGIN_DB_IP, port=LOGIN_DB_PORT,
                               charset=DB_CHARSET, db=LOGIN_DB_NAME)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res is None:
            print "没有找到相关记录，请检查服务器id: %d 是否正确" % server_id
            exit(100)
        else:
            return res[0].encode("utf8")
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def is_port_opened(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print "start, ip %s, port %d" % (ip, int(port))
        s.connect((ip, int(port)))
        print "stop"
        s.shutdown(2)
        return True
    except socket.error as e:
        return False


def shutdown_single_game(ip, server_id, ssh_port=22):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        private_key = paramiko.RSAKey.from_private_key_file(RAS_KEY_FILE)
        ssh_client.connect(ip, port=ssh_port, pkey=private_key)
        cmd = os.path.join(game_server_dir(server_id), "script", "stop_gs.sh")
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        stdout_content = stdout.read()
        stderr_content = stderr.read()
        if not stderr_content:
            print stdout_content.strip("\n")
        else:
            print stderr_content.strip("\n")
        ssh_client.close()
    except paramiko.SSHException as ssh_error:
        print "connection error:%s" % ssh_error


def startup_single_game(ip, server_id, ssh_port=22):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        private_key = paramiko.RSAKey.from_private_key_file(RAS_KEY_FILE)
        ssh_client.connect(ip, port=ssh_port, pkey=private_key)
        cmd = os.path.join(game_server_dir(server_id), "script", "start_gs.sh")
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        stdout_content = stdout.read()
        stderr_content = stderr.read()
        if not stderr_content:
            print stdout_content.strip("\n")
        else:
            print stderr_content.strip("\n")
        ssh_client.close()
    except paramiko.SSHException as ssh_error:
        print "connection error:%s" % ssh_error


def game_server_cn_name(server_id):
    """根据游戏服务器id返回游戏服务器的名字

    :return: string 游戏服务器名字zone_
    """
    sql = "SELECT s_name FROM server where s_id = %d" % server_id
    try:
        conn = MySQLdb.connect(user=LOGIN_DB_USER, passwd=LOGIN_DB_PSW,
                               host=LOGIN_DB_IP, port=LOGIN_DB_PORT,
                               charset=DB_CHARSET, db=LOGIN_DB_NAME)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res is None:
            print "没有找到相关记录，请检查服务器id: %d 是否正确" % server_id
            exit(100)
        else:
            return res[0].encode("utf8")
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def shutdown_all_server(all_server_id, ssh_port=22):

    shutdown_list = []
    failed_shutdown_list = []

    for server_id in all_server_id:
        if is_port_opened(game_server_address(server_id), game_server_port(server_id)):
            print "检测到%s是开启的，正在关闭服务器" % game_server_cn_name(server_id)
            shutdown_list.append(server_id)
            shutdown_single_game(game_server_address(server_id), server_id, ssh_port)
        else:
            print "服务器%s已经关闭" % game_server_cn_name(server_id)

    if shutdown_list:
        for server_id in shutdown_list:
            if not is_port_opened(game_server_address(server_id), game_server_port(server_id)):
                print "关闭%s服务器成功" % game_server_cn_name(server_id)
            else:
                failed_shutdown_list.append(server_id)

    return failed_shutdown_list


if __name__ == "__main__":
    print shutdown_all_server(all_server_list())



