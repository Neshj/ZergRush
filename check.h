#ifndef CHECK_PY
#define CHECK_PY 											\
"#!/usr/bin/python\n" 										\
"import sys\n" 												\
"\n"														\
"if len(sys.argv) != 2:\n"									\
"	print \"Usage: %s <file>\\n\" % sys.argv[0]\n"			\
"	exit(0)\n"												\
"\n"														\
"with open(sys.argv[1], \"r\") as f: magic = f.read(4)\n"	\
"\n"														\
"if (magic == \"\\x7FELF\"):\n"								\
"	print \"ELF File!\"\n"									\
"	exit(-1)\n"												\
"exit(0)\0"

#endif