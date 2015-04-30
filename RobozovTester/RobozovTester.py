# -*- coding: utf-8 -*-

import socket
import json

class RobozovTester:


    def __init__(self,server_ip,server_port):
        self._server_ip = server_ip
        self._server_port = server_port

        print("Server ip: " + self._server_ip)
        print("Server port: " + self._server_port)

    def send_led_blink_datagram(self,time):
        dict_data = {}

        dict_data["msg_type"] = 1
        dict_data["msg_data"] = 2000
        data_str = json.dumps(dict_data)

        self.send_udp_datagram(data_str)

    def send_general_datagram(self,data):
        dict_data = {}

        dict_data["msg_type"] = 2
        dict_data["msg_data"] = data
        data_str = json.dumps(dict_data)

        self.send_udp_datagram(data_str)

    def send_udp_datagram(self,data):
        print ("Sending data: " + data)
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto(data, (self._server_ip,int(self._server_port)))
