# -*- coding: utf-8 -*-
from RobozovTester import *

def startTest():
    tester = RobozovTester("192.168.0.111","30000")
    tester.send_general_datagram("Hello World!!")

    for i in range(1,11):
        tester.send_general_datagram(str(i))

    # Send led blink message
    tester.send_led_blink_datagram(1000)
    tester.send_led_blink_datagram(500)
    tester.send_led_blink_datagram(2000)

startTest()