CC=gcc

# General compiler flags
CFLAGS=-fstack-protector-all -s -fvisibility=hidden -fPIC
LFLAGS=-fPIE -pie -lrt

# Sources list
SOURCES = wrapper.c frag.c report.c 

# Set the object file names, with the source directory stripped
# from the path, and the build path prepended in its place
SERV_OBJECTS = $(SOURCES:%.c=%.server.o)
CLIENT_OBJECTS = $(SOURCES:%.c=%.client.o)

# Main rule, checks the executable and symlinks to the output
all: server client
	@echo "\033[1;34mDone\033[0m"

emulate:
	@make EMULATE=EMULATE

# Removes all build files
clean:
	@rm -f *.o
	@rm -f server
	@rm -f client
	@echo "\033[1;34mClean\033[0m"

server: export DEFS=-DSERVER -DDEFRAG $(A)

# Link the executable
server: $(SERV_OBJECTS)
	@echo "Linking: \033[0;32m$@\033[0m"

ifeq ($(EMULATE),EMULATE)
	@echo "Linking Emulated version"
else
	@echo "Linking Regular version"
endif
	@$(CC) $(SERV_OBJECTS) $(LFLAGS) -o $@


%.server.o: %.c
	@echo "Compiling \033[0;31m$<\033[0m"
ifeq ($(EMULATE),EMULATE)
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS)
else
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS) -DRPI
endif

client: export DEFS=-DDEFRAG $(A)

# Link the executable
client: $(CLIENT_OBJECTS)
	@echo "Linking: \033[0;32m$@\033[0m"
ifeq ($(EMULATE),EMULATE)
	@echo "Linking Emulated version"
	@$(CC) $(CLIENT_OBJECTS) $(LFLAGS) -o $@
else
	@echo "Linking Regular version"
	@$(CC) $(CLIENT_OBJECTS) $(LFLAGS) -o $@ -lwiringPi
endif



%.client.o: %.c
	@echo "Compiling \033[0;31m$<\033[0m"
ifeq ($(EMULATE),EMULATE)
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS)
else
	@$(CC) $(CFLAGS) -c $< -o $@ $(DEFS) -DRPI
endif
