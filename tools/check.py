#!/usr/bin/python
import sys

if len(sys.argv) != 2:
	print "Usage: %s <file>\n" % sys.argv[0]
	exit(0)

with open(sys.argv[1], "r") as f: magic = f.read(4)

if (magic == "\x7FELF"):
	print "ELF File!"
	exit(-1)
exit(0)  