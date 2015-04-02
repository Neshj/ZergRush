CC=gcc

# General compiler flags
CFLAGS=-fstack-protector-all -O3 -s -fvisibility=hidden
LFLAGS=-fPIE -pie

# Sources list
SOURCES = wrapper.c frag.c report.c 

all: server client

server:
	$(CC) -o $@ $(CFLAGS) $(LFLAGS) $(SOURCES) -DSERVER -DDEFRAG

client:
	$(CC) -o $@ $(CFLAGS) $(LFLAGS) $(SOURCES) -DDEFRAG

clean:
	@rm server
	@rm client
