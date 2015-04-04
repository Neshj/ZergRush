#!/usr/bin/python
from struct import pack

MAX_PACKET_SIZE = 64

class Protocol:
	HandleDataRequest = 0
	HandleKARequest = 1
	HandleFileRequest = 2
	HandlePidRequest = 3
	HandleVariablesRequest = 4
	HandleUpperRequest = 5

	kRequest = 0
	kRespone = 1

	def __init__(self, packet, msg_type, direction = kRequest):
		self.pkt = packet
		self.type = msg_type
		self.direction = direction

	def serialize(self):
		return pack("II", self.type, self.direction) + self.pkt

class ProtocolHandleUpper(Protocol):
	def __init__(self, path, payload):
		# Call parent ctor to init general variables
		Protocol.__init__(self, pack("I%dsI" % len(path), len(path), path, len(payload)) + payload, Protocol.HandleUpperRequest)

class Packet:
	def __init__(self, original_size, payload, id = 0, frag_idx = 0):
		if len(payload) > MAX_PACKET_SIZE:
			raise Exception("Payload size cannot be greater than %d" % MAX_PACKET_SIZE)

		self.src = 0
		self.dst = 0
		self.id = id
		self.frag_idx = frag_idx
		self.original_size = original_size
		self.payload = payload

		# Pad with NULLs if it does not reach the appropriate size.
		if len(payload) != MAX_PACKET_SIZE:
			self.payload += "\x00" * (MAX_PACKET_SIZE - len(self.payload))

	def serialize(self):
		return pack("IIIII", self.src, self.dst, self.original_size, self.id, self.frag_idx) + self.payload

class FragmentedPacket:
	def __init__(self, original):
		if (original.__class__ is Packet):
			original = original.payload
		elif isinstance(original, Protocol):
			original = original.serialize()

		self.orig = original
		self.fragments = []

		# Fragment packet
		self.frag()

	def frag(self):
		pkt = self.orig
		fragments_num = len(pkt) / MAX_PACKET_SIZE

		if len(pkt) % MAX_PACKET_SIZE != 0:
			fragments_num += 1

		for i in xrange(fragments_num):
			self.fragments.append(Packet(len(pkt), \
						pkt[i * MAX_PACKET_SIZE : (i + 1) * MAX_PACKET_SIZE], \
						frag_idx = i))