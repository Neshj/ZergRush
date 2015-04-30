#!/usr/bin/python

'''
	Simple udp socket server
	Silver Moon (m00n.silv3r@gmail.com)
'''

from scapy.all import *
import RPi.GPIO as GPIO
from time import sleep
import json

# Network definitions

HOST = ''	    # Symbolic name meaning all available interfaces
PORT = 30000	# Arbitrary non-privileged port
SERVER_IP  = "192.168.0.111"
ROBOT_PORT = 30000

# LED definitions

PIN_LED   = 18
SLEEP     = 0.5
STATE_ON  = True
STATE_OFF = False
STATES    = { True  : "ON",
              False : "OFF" }

def init():	
    # Needs to be BCM. GPIO.BOARD lets you address GPIO ports by periperal
    # Connector pin number, and the LED GPIO isn't on the connector
    GPIO.setmode(GPIO.BCM)

    # set up GPIO output channelo
    GPIO.setup(PIN_LED, GPIO.OUT)
		
    print "GPIO setup complete"

def my_filter(packet):
    if (packet[IP].proto == "udp" and 
	packet[IP].src == SERVER_IP and
       	packet[UDP].dport == ROBOT_PORT):
        return 1
    return 0

## Define our Custom Action function
def customAction(packet):

    global packetCount
    packetCount += 1
    
    if (my_filter(packet)):
        # Handle packet
        packet.show2()
        return 1

    return 0

def set_led(state):
    print "LED %d STATE: %s" % (PIN_LED, STATES[state])
    GPIO.output(PIN_LED, state)

def main():
    # initialize
    init()
                
    global packetCount
    packetCount = 0

    ## Setup sniff, filtering for IP traffic
    sniff(filter="udp", prn=customAction)

if __name__ == "__main__":
    main()

