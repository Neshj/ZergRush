CC=gcc

# General compiler flags
CFLAGS=-fstack-protector-all -s -fvisibility=hidden -fPIC
LFLAGS=-fPIE -pie -lrt

ifdef RPI
LFLAGS+= -lwiringPi
endif

# Sources list
SOURCES = wrapper.c frag.c report.c 

# Set the object file names, with the source directory stripped
# from the path, and the build path prepended in its place
SERV_OBJECTS = $(SOURCES:%.c=%.server.o)
CLIENT_OBJECTS = $(SOURCES:%.c=%.client.o)

# Main rule, checks the executable and symlinks to the output
all: server client
	@echo "\033[1;34mDone\033[0m"

# Removes all build files
clean:
	@rm -f *.o
	@rm -f server
	@rm -f client
	@echo "\033[1;34mClean\033[0m"

server: export DEFS=-DSERVER -DDEFRAG -DRPI $(A)

# Link the executable
server: $(SERV_OBJECTS)
	@echo "Linking: \033[0;32m$@\033[0m"
	@$(CC) $(SERV_OBJECTS) $(LFLAGS) -o $@

%.server.o: %.c
	@echo "Compiling \033[0;31m$<\033[0m"
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS)

client: export DEFS=-DDEFRAG -DRPI $(A)

# Link the executable
client: $(CLIENT_OBJECTS)
	@echo "Linking: \033[0;32m$@\033[0m"
	@$(CC) $(CLIENT_OBJECTS) $(LFLAGS) -o $@

%.client.o: %.c
	@echo "Compiling \033[0;31m$<\033[0m"
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS)
