#! /usr/bin/env python
# -*- coding: utf-8 -*-
# test version


import SocketServer
import user_info_pb2


class MyAppTCPServer(SocketServer.TCPServer):
    allow_reuse_address = True


class APPTCPHandler(SocketServer.BaseRequestHandler):
    """
    处理用户注册

    """

    def handle(self):
        """
        实际处理函数
        :return:
        """
        client_info = self.request.getpeername()
        print "client address:%s, port number:%d" % (client_info[0], client_info[1])
        data = self.request.recv(1024)
        user_info = user_info_pb2.User()
        user_info.ParseFromString(data)
        print "{} wrote:".format(self.client_address[0])
        print "用户的电话号码: %d" % user_info.phone_number
        print "用户安卓平台id: %d" % user_info.android_platform_id
        print "用户苹果平台id: %d" % user_info.apple_platform_id
        # print user_info.android_platform_id
        # print user_info.apple_platform_id
        # self.request.sendall(user_info.phone_number)
        # self.request.sendall(user_info.android_platform_id)
        # self.request.sendall(user_info.apple_platform_id)


if __name__ == "__main__":

    HOST, PORT = "", 61000

    server = MyAppTCPServer((HOST, PORT), APPTCPHandler)

    server.serve_forever()


