#include <stdbool.h> /*for bool type, true and false values*/
#include <strings.h> /*bzero, memcpy, memset*/
#include <stdint.h> /*for uint*_t types*/
#include <poll.h> /*poll, POLLING */
#include <stdlib.h> /*ssize_t, EXIT_SUCCESS, EXIT_FAILURE */
#include <stdio.h> /*for printf*/
#include <sys/socket.h> /*socket*/
#include <string.h> /*memset*/
#include <errno.h> /*errno, perror*/
#include <unistd.h> /*sleep, getpid*/
#include <netdb.h> /*struct addrinfo*/
#include <fcntl.h> /*O_RDONLY*/
#include <linux/limits.h> /*PATH_MAX*/
#include <sys/wait.h> /*wait*/
#include <signal.h> /* for destruction */

#if defined(RPI) && !defined(SERVER)
#include <wiringPi.h>
#endif

#include "report.h"

#ifdef DEFRAG
	#include "common.h"

	extern void init_collectors();
	frag_e collect_packets(uint8_t * pkt_buffer, uint32_t pkt_len, uint8_t ** o_full_packet, uint32_t * o_full_packet_size);
	extern uint8_t ** break_packet(uint8_t * packet, uint32_t size, uint32_t src, uint32_t dst, uint32_t * o_frags);
#endif

#define CMD_LEN 128

#define DEBUG(X) X

#define to "malloc"

#define MAX_BUFFER 1400

#define UNLIKELY(x) __builtin_expect((x), 1)

/*Yay! Unportable macros (because ({}) is a gcc c extension)*/

#define CHECK_NOT_M1(res, e, msg) CHECK_OR_DIE(res, e, -1, msg)

#define CHECK_OR_DIE(res, expression, expected, msg) { 			\
				res = expression;			\
				if(UNLIKELY(res == expected))		\
				{					\
					perror(msg);			\
					exit(EXIT_FAILURE);		\
				}					\
			}		

typedef enum {
	DATA_MSG = 0,
	KA_MSG,
	FILE_MSG,
	PID_MSG,
	VARS_MSG,
	UPPER_MSG,
	MAX_MSG_TYPE
} MessageType;

typedef enum {
	kRequest = 0,
	kResponse
} RRType;


typedef struct VariableNode_t
{
	char *name;
	char *value;
	struct VariableNode_t *next;
	struct VariableNode_t *prev;
} VariableNode;


typedef struct {
	int simple_socket_server;
	int wrapper_socket_server;
	int simple_socket_client;
	int wrapper_socket_client;

#ifdef SERVER
	int control_socket_client;
	int control_socket_server;
#endif

} connection_t;

VariableNode *VaraiblesList;

#define ADD_TO_BUFFER_SIZE(p, currsize, from, size) 	{	 							\
															memcpy(p, from, size);		\
															currsize += size;			\
															p += size;					\
														}

#define ADD_TO_BUFFER(p, currsize, from) 	{	 										\
												memcpy(p, &from, sizeof(from));			\
												currsize += sizeof(from);				\
												p += sizeof(from);						\
											}


#define GET_FROM_BUFFER_SIZE(p, to, size)	{ 							\
												memcpy(to, p, size);	\
												p += size;				\
											}

#define GET_FROM_BUFFER(p, to)	{	 								\
									memcpy(&to, p, sizeof(to));		\
									p += sizeof(to);				\
								}


#define ADD_HEADER_TO_BUFFER(p, currsize, mt, rr)	{											\
														ADD_TO_BUFFER (p, currsize, mt);		\
														ADD_TO_BUFFER (p, currsize, rr);		\
													}

void print_hex(uint8_t * buf, uint32_t size);

static inline bool SendHelper(int sockfd, const uint8_t *buffer, uint32_t size, uint32_t *sent_bytes)
{
	ssize_t res;

	res = send(sockfd, buffer, size, 0);

	BLINK(ORANGE_PIN, 0, NORMAL_BLINK);

	if (res == -1)
	{
		switch (errno)
		{
			case ECONNREFUSED:
				/*Connection failed should reconnect*/
				perror("Send to simple socket failed");
				/*close(connection->simple_socket);*/
				return false;
			default:
				perror("Send to simple socket failed");
				exit(EXIT_FAILURE);
		}
	}

	*sent_bytes = (uint32_t) res;

	return *sent_bytes == size;
}

static bool SendHelperFrag(int sockfd, uint8_t *buffer, uint32_t size, uint32_t *sent_bytes)
{
#ifdef DEFRAG
	uint32_t num_of_frags, i, temp_sent_bytes = 0;
	bool status = false;
	uint8_t **frags;

/*
	printf("Received buffer:\n");
	print_hex(buffer, size);
*/
	frags = break_packet(buffer, size, 0xAABBCCDD, 0x00112233, &num_of_frags);
	for(i=0; i<num_of_frags; i++)
	{
		status = SendHelper(sockfd, frags[i], MAX_PACKET_SIZE + sizeof(hdr_t), &temp_sent_bytes );
/*
		print_hex(frags[i], MAX_PACKET_SIZE + sizeof(hdr_t));
*/
		*sent_bytes += temp_sent_bytes;

		if (status == false)
			break;

	}

	for(i=0; i<num_of_frags; i++)
	{
		free(frags[i]);
	}

	return status;
#else
	return SendHelper(sockfd, buffer, size, sent_bytes);

#endif

}

static bool SendKA(const connection_t *connection, const uint8_t *payload, uint32_t payload_size, RRType KA_type)
{
	uint8_t *buffer, *current;
	MessageType mt = KA_MSG;
	uint32_t sent_bytes, size = payload_size + sizeof(mt) + sizeof(KA_type) + sizeof(size);

	buffer = malloc(size);
	if (buffer == NULL)
		return false;

	memset(buffer, 0, size);

	current = buffer;
	size = 0;

	ADD_HEADER_TO_BUFFER(current, size, mt, KA_type);
		
	ADD_TO_BUFFER(current, size, payload_size);

	ADD_TO_BUFFER_SIZE(current, size, payload, payload_size);
	
	if (SendHelperFrag(connection->wrapper_socket_client, buffer, size, &sent_bytes) == false)
		return false;

	DEBUG(printf("Sent %d bytes to wrapper\n", sent_bytes);)
 
	free(buffer);

	return sent_bytes == size;
}

static bool HandleKARequest(const connection_t *connection, const uint8_t *packet, uint32_t packet_size)
{
	const uint8_t *payload;
	uint32_t size;

	if (packet == NULL)
		return false;
	if (packet_size < sizeof(size))
	{
		DEBUG (printf("KA request invalid: expected %d bytes, got %d bytes\n", sizeof(size), packet_size ););
		return false;
	}

	payload = packet;

	GET_FROM_BUFFER(payload, size);

	return SendKA(connection, payload, size, kResponse );
}

static bool HandleFileRequest(const connection_t *connection, const uint8_t *packet, uint32_t packet_size)
{
	pid_t pid;
	char temp_string[32];
	uint8_t buffer[MAX_BUFFER], *current;
	int f;
	ssize_t res;
	uint32_t sent_bytes, size, len;
	MessageType mt = FILE_MSG;
	RRType rr = kResponse;

	if (packet == NULL)
		return false;
	if (packet_size > PATH_MAX || packet_size >= MAX_BUFFER)
		return false;

	pid = getpid();

	memset(temp_string, 0, sizeof(temp_string));
	sprintf(temp_string, "/proc/%d/", pid);
	len = strlen(temp_string);

	strncpy(temp_string + len, ((char *)packet) + len, packet_size - len);

	if (strncmp(temp_string, (char *)packet, len) != 0)
		return false;

	current = buffer;
	size = 0;

	ADD_HEADER_TO_BUFFER(current, size, mt, rr);

	f = open(temp_string, O_RDONLY);
	CHECK_NOT_M1(res, read(f, current, MAX_BUFFER - size), "Read failed");
	close(f);
	
	return SendHelperFrag(connection->wrapper_socket_client, buffer, res + 2, &sent_bytes);

}


static bool HandlePidRequest(const connection_t *connection, const uint8_t *packet, __attribute__ ((unused)) uint32_t packet_size)
{
	pid_t pid;
	uint8_t buffer[MAX_BUFFER], *current;
	uint32_t sent_bytes, size;
	MessageType mt = PID_MSG;
	RRType rr = kResponse;

	if (packet == NULL)
		return false;

	pid = getpid();
	
	current = buffer;
	size = 0;

	ADD_HEADER_TO_BUFFER(current, size, mt, rr);
	ADD_TO_BUFFER(current, size, pid);

	return SendHelperFrag(connection->wrapper_socket_client, buffer, size, &sent_bytes);

}


static bool AddVariable(VariableNode **firstNode, char *name, char *value)
{
	VariableNode *node = *firstNode;
	VariableNode *curr_node = *firstNode;
	VariableNode *new_node;

	if (node == NULL)
	{
		new_node = malloc(sizeof(VariableNode));
		if (new_node == NULL)
			return false;

		new_node->prev = NULL;
		new_node->value = value;
		new_node->name = name;
		new_node->next = NULL;

		*firstNode = new_node;
		return true;
	}

	while(curr_node->next != NULL)
	{

		if (strcmp(name, curr_node->name) == 0)
		{
			free(curr_node->value);
			curr_node->value = value;
			return true;
		}
		curr_node = curr_node->next;
	}

	if (strcmp(name, curr_node->name) == 0)
	{
		free(curr_node->value);
		curr_node->value = value;
		return true;
	}


	new_node = malloc(sizeof(VariableNode));
	if (new_node == NULL)
		return false;

	curr_node->next = new_node;

	new_node->prev = curr_node;
	new_node->value = value;
	new_node->name = name;
	new_node->next = NULL;

	return true;


}

static void RemoveVariable(VariableNode *node, char *name)
{
	VariableNode *curr_node = node;

	if (node == NULL)
		return;

	if (strcmp(name, curr_node->name) == 0 )
	{
		curr_node->next->prev = NULL;

		free(curr_node->name);
		free(curr_node->value);
		free(curr_node);

		return;
	}

	while(curr_node->next != NULL)
	{
		if (strcmp(name, curr_node->name) == 0)
		{
			free(curr_node->name);
			free(curr_node->value);
			curr_node->next->prev = curr_node->prev;
			curr_node->prev->next = curr_node->next;

			return;
		}
		curr_node = curr_node->next;
	}

	if (strcmp(name, curr_node->name) == 0 )
	{
		free(curr_node->name);
		free(curr_node->value);
		free(curr_node->prev->next = NULL);
		free(curr_node);
	}
}

static bool HandleSetVariableRequest(__attribute__((unused)) const connection_t *connection, const char *payload, uint32_t payload_size)
{
	uint32_t name_len = 0, value_len = 0, i;
	char *name, *value;

	printf("payload_size: %d\n", payload_size);

	for(i=0; i < payload_size; i++)
	{
		if (payload[i] == ' ')
		{
			name_len = i;
			break;
		}
	} 

	if (name_len == payload_size || name_len == 0)
		return false;

	name = malloc(name_len+1);
	if (name == NULL)
		return false;

	strncpy(name, payload, name_len);
	name[name_len] = '\0';

	value_len = payload_size - name_len;
 
	if (value_len == 0)
		return false;

	value = malloc(value_len+1);
	if (value == NULL)
		return false;

	strncpy(value, payload + name_len + 1, value_len);
	value[value_len] = '\0';

	AddVariable(&VaraiblesList, name, value);

	return true;
}

static bool HandleDelVariableRequest(__attribute__((unused)) const connection_t *connection, const char *payload, uint32_t payload_size)
{
	uint32_t name_len = payload_size;
	char *name;

	if (name_len == 0)
		return false;

	name = malloc(name_len+1);
	if (name == NULL)
		return false;

	strncpy(name, payload, name_len);
	name[name_len] = '\0';

	RemoveVariable(VaraiblesList, name);

	free(name);

	return true;
}


static uint32_t ListToString(VariableNode *node, char *buffer, uint32_t buffer_size)
{
	uint32_t size = 0, len;
	char *current =  buffer;
	VariableNode *curr_node = node;

	while(curr_node != NULL)
	{
		len = strlen(curr_node->name) + strlen(curr_node->value) + strlen(" : \n");
		if (size + len > buffer_size)
		{
			printf("Over %d %d\n", size + len, buffer_size);
			return size;
		}

		sprintf(current, "%s : %s\n", curr_node->name, curr_node->value);

		current += len;
		size += len;

		curr_node = curr_node->next;

	}
	printf("Done\n");

	return size;
}

static bool HandleShowRequest(const connection_t *connection)
{

	uint8_t buffer[MAX_BUFFER], *current;
	uint32_t sent_bytes, size;
	MessageType mt = VARS_MSG;
	RRType rr = kResponse;

	current = buffer;
	size = 0;

	ADD_HEADER_TO_BUFFER(current, size, mt, rr);

	size += ListToString(VaraiblesList, (char *)current, MAX_BUFFER);

	return SendHelperFrag(connection->wrapper_socket_client, buffer, size, &sent_bytes);
	
}

static bool HandleVariablesRequest(const connection_t *connection, const uint8_t *packet, uint32_t packet_size)
{
	const uint8_t *payload = packet;
	uint32_t stringSize;

	if (packet == NULL)
		return false;
	
	GET_FROM_BUFFER(payload, stringSize);

	if (packet_size < stringSize + sizeof(stringSize))
	{
		DEBUG(printf("Incorrect size. Expected at least %d got %d\n", stringSize + sizeof(stringSize), packet_size );)
		return false;
	}

	DEBUG(printf("Variables: got %s\n", payload););

	if (strncmp((char *)payload, "SHOW", 4) == 0)
		return HandleShowRequest(connection);

	if (strncmp((char *)payload, "SET ", 4) == 0)
		return HandleSetVariableRequest(connection, (const char*)payload + 4, stringSize - 4);
	if (strncmp((char *)payload, "DEL ", 4) == 0)
		return HandleDelVariableRequest(connection, (const char*)payload + 4, stringSize - 4);


	return false;

}

#define TKN "."

static inline int find_pta(char * path, uint32_t len)
{
	/* Variable definition */
	uint32_t i;

	/* Code section */
	if (len == 1)
		return 0;

	for (i = 0; i < len - 1; ++i)
	{
		if (path[i] == ' ')
		{
			printf("SPACE!!!!!!!!!!!!!\n");
			return 1;
		}

		if ((path[i] == TKN[0]) && (path[i + 1] == TKN[0]))
		{
			printf("DOTSS!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
			return 1;
		}
	}

	return 0;
}

#define FILES_DIR "k"

static bool HandleUpperRequest(__attribute__((unused)) const connection_t *connection, const uint8_t *packet, __attribute__((unused)) uint32_t packet_size)
{
	const uint8_t *payload = packet;
	uint32_t pathSize, fileSize;
	
	/* Variable definition */
	#define CHECK_PROG "./tools/check.py"
	int ret, fd;
	char system_cmd[CMD_LEN + sizeof(CHECK_PROG) + 2];
	char path[CMD_LEN + 1];
	char full_path[CMD_LEN + 1];
	char cwd[PATH_MAX + 1];

	if (packet == NULL)
		return false;
	
	GET_FROM_BUFFER(payload, pathSize);
	GET_FROM_BUFFER_SIZE(payload, &path, pathSize);
	GET_FROM_BUFFER(payload, fileSize);

	/* NULL Terminate the path just in case */
	path[pathSize] = '\0';

	/* Filter the path. No directory traversals. */
	if (find_pta(path, strnlen(path, CMD_LEN)))
	{
		printf("Path traversal detected! (%s)\n", path);
		return false;
	}

	/* Get cwd */
	getcwd(cwd, PATH_MAX);

	snprintf(full_path, CMD_LEN, "%s/%s/%s", cwd, FILES_DIR, path);

	/* Write the given data to a file */
	if ((fd = open(full_path, O_CREAT | O_RDWR, S_IRWXU)) < 0)
	{
		perror("Failed opening file");

		return false;
	}

	if (write(fd, (uint8_t *)(payload), fileSize ) <= 0)
	{
		perror("Error writing file");
		printf("%s %p %d\n", path, payload, fileSize);
		printf("%s\n", payload + 1);
		return false;
	}

	close(fd);

	/* Check if this file is OK */
	snprintf(system_cmd, CMD_LEN + sizeof(CHECK_PROG) + 2, "%s %s", CHECK_PROG, full_path);

	/* Call checker */
	ret = system(system_cmd);

	if (ret != 0)
	{
		printf("Malicious file (%d).\n", ret);

		unlink(full_path);

		return false;
	}

	return true;

}


#ifdef SERVER

static bool HandleControl(const connection_t *connection)
{
	uint8_t buffer[MAX_BUFFER];
	uint32_t recved_bytes, sent_bytes;
	ssize_t res;

	memset(buffer, 0, sizeof(buffer));

	CHECK_NOT_M1(res, recv(connection->control_socket_server, buffer, MAX_BUFFER, 0), "recv from wrapper socket failed");
	recved_bytes = (uint32_t) res;

	BLINK(ORANGE_PIN, 0, NORMAL_BLINK);

	DEBUG(printf("Control receved %d bytes\n", recved_bytes);)

	if (SendHelperFrag(connection->wrapper_socket_client, buffer, recved_bytes, &sent_bytes) == false)
		return false;

	DEBUG(printf("Sent %d bytes to wrapper\n", sent_bytes);)

	return true;
}

#endif

static bool HandleSimpleServer(const connection_t *connection)
{
	uint8_t buffer[MAX_BUFFER + 1], *current;
	uint32_t recved_bytes, sent_bytes;
	ssize_t res;
	uint32_t size = 0;
	MessageType mt = DATA_MSG;
	RRType rr = kRequest;

	memset(buffer, 0, sizeof(buffer));

	current = buffer;

	ADD_HEADER_TO_BUFFER(current, size, mt, rr);

	CHECK_NOT_M1(res, recv(connection->simple_socket_server, current, MAX_BUFFER, 0), "recv from wrapper socket failed");

	recved_bytes = (uint32_t) res;

	DEBUG(printf("Simple receved %d bytes\n", recved_bytes);)

	if (SendHelperFrag(connection->wrapper_socket_client, buffer, recved_bytes + size, &sent_bytes) == false)
		return false;

	DEBUG(printf("Sent %d bytes to wrapper\n", sent_bytes);)

	return true;
}

static bool HandleDataRequest(const connection_t *connection, const uint8_t *packet, uint32_t packet_size)
{
	uint32_t sent_bytes;

	if (SendHelper(connection->simple_socket_client, packet, packet_size, &sent_bytes) == false)
		return false;

	DEBUG(printf("Sent %d bytes to simple\n", sent_bytes);)

	return sent_bytes == packet_size;
}

typedef bool (*HandleType) (const connection_t*, const uint8_t *, uint32_t);

static const HandleType HandleArray[6] = 	{
											HandleDataRequest,		
											HandleKARequest,		
											HandleFileRequest,		
											HandlePidRequest,		
											HandleVariablesRequest,
											HandleUpperRequest
										};

#ifdef DEFRAG
#define CLEANUP(x,ret) 	{					\
							free(x);		\
							return ret;		\
						}
#else
#define CLEANUP(x,ret)	return ret;
#endif

static bool HandleWrapperServer(const connection_t *connection)
{
	uint8_t *payload, *receved_buffer;
	uint8_t  buffer[MAX_BUFFER];
	MessageType mt;
	RRType rr;
	uint32_t recved_bytes, full_packet_size;
#ifdef SERVER
	uint32_t sent_bytes;
#endif
	ssize_t res;
	bool status = false;
#ifdef DEFRAG
	frag_e f;
#endif
	memset(buffer, 0, sizeof(buffer));

	CHECK_NOT_M1(res, recv(connection->wrapper_socket_server, buffer, MAX_BUFFER, 0), "recv from wrapper socket failed");
	recved_bytes = (uint32_t) res;

#ifdef DEFRAG

	f = collect_packets(buffer, recved_bytes, &receved_buffer, &full_packet_size);

	if (f == E_ERR)
		return false;
	if (f == E_FRAG)
		return true;

	recved_bytes = full_packet_size;

	payload = receved_buffer;

#else

	payload = buffer;

#endif

	DEBUG(printf("Receved %d bytes from wrapper\n", recved_bytes);)

	if (recved_bytes < sizeof(mt) + sizeof(rr))
		CLEANUP(receved_buffer, false);

	GET_FROM_BUFFER(payload, mt);

	GET_FROM_BUFFER(payload, rr);

	DEBUG(printf("Msg type is: %d\n", mt));

#if SERVER

	if (rr == kResponse)
	{
		if (SendHelper(connection->control_socket_client, buffer, recved_bytes, &sent_bytes) == false)
			CLEANUP(receved_buffer, false);

		DEBUG(printf("Sent %d bytes to control\n", sent_bytes);)	
		CLEANUP(receved_buffer, false);
	}

#endif

	if (rr != kRequest)
	{
		DEBUG (printf("Msg is not a request. Expected %x got %x\n", kRequest, rr ););
		CLEANUP(receved_buffer, false);
	}

	if (mt >= MAX_MSG_TYPE)
	{
		DEBUG (printf("Msg is invalid. Max %x got %x\n", MAX_MSG_TYPE, mt ););
		CLEANUP(receved_buffer, false);
	}

	status = HandleArray[mt](connection, payload, recved_bytes - sizeof(mt) - sizeof(rr));

	CLEANUP(receved_buffer, status);
}

static bool InitSimpleSocketServer(int *sock_result, const char *hostPort)
{	
	int sockfd, res;
	struct addrinfo hints, *result;

	*sock_result = -1;

	memset(&hints, 0, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_flags = AI_PASSIVE; /* TODO: check if needed with SOCK_DGRAM */
	hints.ai_protocol = 0;
	hints.ai_canonname = NULL;
	hints.ai_addr = NULL;
	hints.ai_next = NULL;

	res = getaddrinfo(NULL, hostPort, &hints, &result);

	if (res != 0)
	{
		fprintf(stderr, "Cannot connect to server: getaddinfo %s\n", gai_strerror(res));
		exit(EXIT_FAILURE);
	}

	if (result == NULL)
	{
		fprintf(stderr, "Cannot connect to server: kernel returned NULL\n");
		exit(EXIT_FAILURE);
	}
#if 0
	if (result->ai_next != NULL)
	{
		fprintf(stderr, "Cannot connect to server - multiple sockets found\n");
		exit(EXIT_FAILURE);
	}
#endif
	CHECK_NOT_M1(sockfd, socket(AF_INET, SOCK_DGRAM, 0), "Simple Socket failed");
	
	CHECK_NOT_M1(res, bind(sockfd, result->ai_addr, result->ai_addrlen), "Simple socket bind failed");
	
	freeaddrinfo(result);

	*sock_result = sockfd;

	return true;
}

static bool InitSimpleSocketClient(int *sock_result, const char *hostIP, const char *hostPort)
{	
	int sockfd, res;
	struct addrinfo hints, *result;

	*sock_result = -1;

	CHECK_NOT_M1(sockfd, socket(AF_INET, SOCK_DGRAM, 0), "Simple Socket failed");

	memset(&hints, 0, sizeof(hints));

	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_flags = 0;
	hints.ai_protocol = 0;

	res = getaddrinfo(hostIP, hostPort, &hints, &result);

	if (res != 0)
	{
		fprintf(stderr, "Cannot connect to server: getaddinfo %s\n", gai_strerror(res));
		exit(EXIT_FAILURE);
	}

	if (result == NULL)
	{
		fprintf(stderr, "Cannot connect to server: kernel returned NULL\n");
		exit(EXIT_FAILURE);
	}
#if 0
	if (result->ai_next != NULL)
	{
		fprintf(stderr, "Cannot connect to server - multiple sockets found\n");
		exit(EXIT_FAILURE);
	}
#endif
	res = connect(sockfd, result->ai_addr, result->ai_addrlen);

	freeaddrinfo(result);

	if (res == -1)
	{
		close(sockfd);
		perror("Cannot connect to server [errno]:");
		switch (errno)
		{
			case ECONNREFUSED:
			case EALREADY:
			case ETIMEDOUT:
			case EINTR:
			case ENETUNREACH:
				return false;
			default:
				exit(EXIT_FAILURE);
		}
	}

	*sock_result = sockfd;


	return true;
}

#define CHECK_RESULT(res, msg)					\
			if (res)							\
			{									\
				printf("%s succeeded\n", msg);	\
				INIT_HYBRID(to);		\
			}									\
			else								\
			{									\
				printf("%s failed\n", msg);		\
				exit(EXIT_FAILURE);				\
			}

#ifdef SERVER

static void ServerTransferLoop(const char *controller_ip, const char *robot_ip, const char *port1, const char *port2, const char *port3, const char *port4)
{
	connection_t connection;
	struct pollfd ufds[3];
	int rv;
	
	connection.wrapper_socket_server = -1;
	connection.wrapper_socket_client = -1;
	connection.simple_socket_server = -1;
	connection.simple_socket_client = -1;
	connection.control_socket_server = -1;
	connection.control_socket_client = -1;

	CHECK_RESULT(InitSimpleSocketClient(&connection.simple_socket_client, controller_ip, port1), "Server: Init simple socket client");
	CHECK_RESULT(InitSimpleSocketServer(&connection.simple_socket_server, port2), "Server: Init simple socket server");
	CHECK_RESULT(InitSimpleSocketClient(&connection.wrapper_socket_client, robot_ip, port3), "Server: Init wrapper socket client");
	CHECK_RESULT(InitSimpleSocketServer(&connection.wrapper_socket_server, port4), "Server: Init wrapper socket server");
#ifdef CONTROL
	CHECK_RESULT(InitSimpleSocketClient(&connection.control_socket_client, "localhost", port5), "Server: Init contorl socket client");
	CHECK_RESULT(InitSimpleSocketServer(&connection.control_socket_server, port6), "Server: Init contorl socket server");
#endif


#ifdef DEFRAG
	init_collectors();
#endif

	printf("Init done!\n");

	ufds[0].fd = connection.wrapper_socket_server;
	ufds[0].events = POLLIN;
	
	ufds[1].fd = connection.simple_socket_server;
	ufds[1].events = POLLIN;
#ifdef CONTROL
	ufds[2].fd = connection.control_socket_server;
	ufds[2].events = POLLIN;
#endif

	while (1)
	{
#ifdef CONTROL
		CHECK_NOT_M1(rv, poll(ufds, 3, 10000), "Transfer loop - poll failed");
#else
		CHECK_NOT_M1(rv, poll(ufds, 2, 10000), "Transfer loop - poll failed");
#endif

		if (rv == 0) /*Timeout!*/
		{
			/*TODO: ka*/;
			DEBUG(printf("Poll timeout!\n");)
		}
		else
		{
			if (ufds[0].revents & POLLIN)
				HandleWrapperServer(&connection);
			if (ufds[1].revents & POLLIN)
				HandleSimpleServer(&connection);
#ifdef CONTROL	
			if (ufds[2].revents & POLLIN)
				HandleControl(&connection);
#endif
		}

	}
}


#else
static void ServerTransferLoop(const char *server_ip, const char *port1, const char *port2, const char *port3, const char *port4)
{
	connection_t connection;
	struct pollfd ufds[3];
	int rv;
	
	connection.wrapper_socket_server = -1;
	connection.wrapper_socket_client = -1;
	connection.simple_socket_server = -1;
	connection.simple_socket_client = -1;

	CHECK_RESULT(InitSimpleSocketClient(&connection.simple_socket_client, "localhost", port1), "Server: Init simple socket client");
	CHECK_RESULT(InitSimpleSocketServer(&connection.simple_socket_server, port2), "Server: Init simple socket server");
	CHECK_RESULT(InitSimpleSocketClient(&connection.wrapper_socket_client, server_ip, port3), "Server: Init wrapper socket client");
	CHECK_RESULT(InitSimpleSocketServer(&connection.wrapper_socket_server, port4), "Server: Init wrapper socket server");

#ifdef DEFRAG
	init_collectors();
#endif

	printf("Init done!\n");

	ufds[0].fd = connection.wrapper_socket_server;
	ufds[0].events = POLLIN;
	
	ufds[1].fd = connection.simple_socket_server;
	ufds[1].events = POLLIN;
	
	while (1)
	{
		CHECK_NOT_M1(rv, poll(ufds, 3, 10000), "Transfer loop - poll failed");

		if (rv == 0) /*Timeout!*/
		{
			/*TODO: ka*/;
			DEBUG(printf("Poll timeout!\n");)
		}
		else
		{
			if (ufds[0].revents & POLLIN)
				HandleWrapperServer(&connection);
			if (ufds[1].revents & POLLIN)
				HandleSimpleServer(&connection);	
		}

	}
}

#endif

static void destructor_handler(__attribute__ ((unused)) int sig,
								__attribute__ ((unused)) siginfo_t *si,
								__attribute__ ((unused)) void *unused)
{
	printf("Caught(%d): %d\n", getpid(), sig);

	DEINIT_HYBRID(to);

	if (sig == SIGINT)
	{
		system("rm -rf tools " FILES_DIR);
	}
	else if (sig == SIGSEGV)
	{
		exit(-42);
	}
}

#include "check.h"

int main(int argc, char **argv)
{
	int fd;
	DEBUG(printf("%d\n", getpid()););


#ifdef SERVER
#if defined(RPI)
	if (argc != 5)
	{
		printf("usage: %s <Remote Control IP> <Robot IP> <Remote Control Port> <Robot Port>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	ServerTransferLoop(argv[1], argv[2], argv[3], argv[3], argv[4], argv[4] );
#else
	if (argc != 7)
	{
		printf("usage: %s <Remote Control IP> <Robot IP> <Remote Control Port SEND> <Remote Control Port RECV> <Robot Port SEND> <Robot Port RECV>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	ServerTransferLoop(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6] );
#endif
#else
	pid_t cpid, w;
	int status;
	struct sigaction sa;
#if defined(RPI) && !defined(SERVER)
	if (argc != 5)
	{
		printf("usage: %s <Server IP> <Server Port> <Simple SEND port (To Robot controller process)> <Simple RECV port (from Robot controller process)>\n", argv[0]);
		exit(EXIT_FAILURE);
	}
#else
	if (argc != 6)
	{
		printf("usage: %s <Server IP> <Server Port SEND> <Server Port RECV> <Simple SEND port (To Robot controller process)> <Simple RECV port (from Robot controller process)>\n", argv[0]);
		exit(EXIT_FAILURE);
	}
#endif

	wiringPiSetup();

	if (!getuid())
		setuid(1000);

	pinMode(BLUE_PIN, OUTPUT);
	pinMode(ORANGE_PIN, OUTPUT);
	pinMode(RED_PIN, OUTPUT);

	sa.sa_flags = SA_SIGINFO;
	sigemptyset(&sa.sa_mask);
	sa.sa_sigaction = destructor_handler;

	if (sigaction(SIGSEGV, &sa, NULL) == -1)
	{
		perror("Error in sigaction");

		return -1;
	}

	if (sigaction(SIGINT, &sa, NULL) == -1)
	{
		perror("Error in sigaction");

		return -1;
	}

	system("rm -rf tools " FILES_DIR);

	/* Setup the env for usage */
	if (mkdir(FILES_DIR, S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH) < 0)
	{
		perror("Error creating drectory for files");

		/* return -1; */
	}

	if (mkdir("tools", S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH) < 0)
	{
		perror("Error creating directory for tools");

		/* return -1; */
	}

	/* Create the check tool every time the process runs */
	if ((fd = open("tools/check.py", O_RDWR | O_CREAT,
				S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH)) < 0)
	{
		perror("Error in creating check tool");

		return -1;
	}

	/* Write the tool */
	write(fd, CHECK_PY, sizeof(CHECK_PY));

	close(fd);

	while (1)
	{
		cpid = fork();

		if(cpid == -1)
		{
			perror("Fork failed");
			exit(EXIT_FAILURE);
		}

		if (cpid == 0)
		{
#if defined(RPI) && !defined(SERVER)
			ServerTransferLoop(argv[1], argv[3], argv[4], argv[2], argv[2]);
#else
			ServerTransferLoop(argv[1], argv[4], argv[5], argv[2], argv[3]);
#endif
		}
		else
		{
			printf("Waiting...\n");
			w = wait(&status);
			printf("Signal caught\n");
			if (w == -1)
			{
				perror("Wait failed");
				exit(EXIT_FAILURE);
			}

			if (WIFEXITED(status))
			{
				printf("Client exited with status %d\n", WEXITSTATUS(status));

				if (WEXITSTATUS(status) == 0)
					exit(EXIT_SUCCESS);

				BLINK(RED_PIN, 5, 0); /* digitalWrite(RED_PIN, HIGH); */
			}
			if (WIFSIGNALED(status))
			{
				printf("Client killed by signal %d\n", WTERMSIG(status));

				BLINK(RED_PIN, 5, 0); /* digitalWrite(RED_PIN, HIGH); */
			}
		}

		REPORT(REPORT_IP, REPORT_PORT);
	}

	destructor_handler(0, NULL, NULL);

#endif

	return EXIT_SUCCESS;
}

