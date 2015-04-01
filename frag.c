#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <sys/un.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/reboot.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/reboot.h>

#include "report.h"

#include "common.h"

typedef struct collector_t
{
	hdr_t ** packets;
	uint32_t fragments;
	uint32_t total_fragments;
	uint32_t fragments_bitmap;
	uint32_t last_update;
	uint32_t packet_size;
	uint32_t id;
	uint8_t available;
} collector_t;

#define BYTES_IN_LINE 16

void print_hex(uint8_t * buf, uint32_t size)
{
	/* Variable definition */
	uint32_t i;
	uint32_t j;

	/* Code section */
	for (i = 0; i < size / BYTES_IN_LINE + (size % BYTES_IN_LINE != 0); ++i)
	{
		for (j = 0; j < (BYTES_IN_LINE * (i + 1) <= size ? BYTES_IN_LINE : size % BYTES_IN_LINE); ++j)
		{
			printf("%02X ", buf[i * BYTES_IN_LINE + j]);
		}

		if (BYTES_IN_LINE * (i + 1) > size)
		{
			for (j = 0; j < BYTES_IN_LINE - size % BYTES_IN_LINE; ++j)
			{
				printf("   ");
			}
		}

		printf("\t");

		for (j = 0; j < (BYTES_IN_LINE * (i + 1) <= size ? BYTES_IN_LINE : size % BYTES_IN_LINE); ++j)
		{
			printf("%c ", buf[i * BYTES_IN_LINE + j]);
		}

		printf("\n");
	}
}

uint32_t g_id = 0;

uint8_t ** break_packet(uint8_t * packet, uint32_t size, uint32_t src, uint32_t dst, uint32_t * o_frags)
{
	/* Variable definition */
	uint8_t ** packets;
	hdr_t * frag;
	uint32_t id = g_id++;
	uint32_t orig_size = size;

	/* Code section */
	/* Allocate memory for the array of fragments */
	packets = malloc(sizeof(hdr_t *));

	/* We at least have one fragment */
	*o_frags = 1;

	do
	{
		/* Allocate memory for the fragment */
		frag = malloc(sizeof(hdr_t) + MAX_PACKET_SIZE);

		/* Clear all previously remaind data */
		memset(frag, 0, sizeof(hdr_t) + MAX_PACKET_SIZE);

		/* Build header */
		frag->size = orig_size;
		frag->id = id;
		frag->frag_idx = *o_frags - 1;
		frag->src = src;
		frag->dst = dst;

		/* Copy the data */
		memcpy((uint8_t *)frag + sizeof(hdr_t), packet, size < MAX_PACKET_SIZE ? size : MAX_PACKET_SIZE);

		/* Set the fragment in the list */
		packets[*o_frags - 1] = (uint8_t *)frag;

		/* Quit loop if we finished processing */
		if (size <= MAX_PACKET_SIZE)
			break;

		/* Advance on the buffer to next fragment */
		packet += MAX_PACKET_SIZE;

		size -= MAX_PACKET_SIZE;

		/* Increase number of fragments */
		(*o_frags)++;

		/* Realloc the array */
		packets = realloc(packets, *o_frags * sizeof(hdr_t *));
	}
	while (size);

	return packets;
}

uint8_t * build_packet(collector_t * collector)
{
	/* Variable definition */
	uint8_t * packet;
	uint32_t i;
	uint32_t total;
	hdr_t ** pkts;

	/* Code section */
	/* Allocate memory for the packet */
	packet = malloc(collector->packet_size);

	/* Get the packets array */
	pkts = collector->packets;

	/* Get total size */
	total = collector->packet_size;

	/* Start building the packet */
	for (i = 0; i < collector->total_fragments; ++i)
	{
		memcpy(packet + pkts[i]->frag_idx * MAX_PACKET_SIZE,
			pkts[i] + 1,
			((pkts[i]->frag_idx == collector->total_fragments - 1) &&
				 (total % MAX_PACKET_SIZE)) ? total % MAX_PACKET_SIZE : MAX_PACKET_SIZE);
	}

	return packet;
}

#define MAX_COLLECTORS 128

collector_t collectors[MAX_COLLECTORS];

void reset_collector(collector_t * collector)
{
	/* Reset the collector */
	collector->packets = NULL;
	collector->fragments = 0;
	collector->fragments_bitmap = 0;
	collector->available = 1;
	collector->last_update = 0;
	collector->packet_size = 0;
	collector->id = 0;
}

void free_fragments(collector_t * collector)
{
	/* Variable definition */
	uint32_t index;

	/* Code section */
	/* Free all fragments */
	for (index = 0; index < collector->fragments; ++index)
	{
		/* Free the fragment */
		free(collector->packets[index]);
	}

	free(collector->packets);

	reset_collector(collector);
}

uint32_t get_available_collector()
{
	/* Variable definition */
	uint32_t index;
	uint32_t lowest_time = 0xffffffff;
	uint32_t lowest_index = 0;

	/* Code section */
	/* Init all the collectors */
	for (index = 0; index < MAX_COLLECTORS; ++index)
	{
		if (collectors[index].available)
			return index;
	}

	/* If there is no available collector - get the collector that was update the least */
	for (index = 0; index < MAX_COLLECTORS; ++index)
	{
		if (collectors[index].last_update < lowest_time)
		{
			lowest_time = collectors[index].last_update;
			lowest_index = index;
		}
	}

	/* Free all it's fragments */
	free_fragments(&collectors[lowest_index]);

	return index;
}

#define ID_WINDOW_SIZE 5

uint32_t last_received_id = 0;

typedef enum
{
	E_NORMAL,
	E_CONTROL
} msg_type_e;

typedef enum
{
	E_CONTROL_NORMAL,
	E_CONTROL_RESTART,
	E_CONTROL_UPDATE_FILE
} msg_control_type_e;

#define CMD_LEN 128

typedef struct 
{
	msg_type_e type;
	msg_control_type_e control_type;
	char cmd[CMD_LEN];
} protocol_t;

void handle_normal_packet(uint8_t * packet, uint32_t len)
{
	/* Handling of normal packet */
}

int find_pta(char * path, uint32_t len)
{
	/* Variable definition */
	uint32_t i;

	/* Code section */
	if (len == 1)
		return 0;

	for (i = 0; i < len - 1; ++i)
	{
		if (path[i] == ' ')
			return 1;

		if ((path[i] == '.') && (path[i + 1] == '.'))
			return 1;
	}

	return 0;
}

#define LINUX_REBOOT_MAGIC1 0xfee1dead

void handle_control_packet(protocol_t * packet, uint32_t len)
{
	/* Variable definition */
	int fd;
	char * path;

	/* Code section */
	/* Handling of control packet packet */
	switch (packet->control_type)
	{
		case E_CONTROL_RESTART:
		{
			/* Need to be called with CAP_SYS_BOOT */
			/* if (reboot(LINUX_REBOOT_MAGIC1, LINUX_REBOOT_MAGIC2C, LINUX_REBOOT_CMD_RESTART, packet->cmd) < 0) */
			if (reboot(atoi(packet->cmd)) < 0)
			{
				printf("Insufficient priviliges?\n");
			}

			break;
		}

		case E_CONTROL_UPDATE_FILE:
		{
			/* Variable definition */
			#define CHECK_PROG "../tools/check"
			int ret;
			char system_cmd[CMD_LEN + sizeof(CHECK_PROG) + 2];

			/* Get the cmd as the file path */
			path = packet->cmd;

			/* NULL Terminate the path just in case */
			path[CMD_LEN - 1] = '\0';

			/* Filter the path. No directory traversals. */
			if (find_pta(path, strnlen(path, CMD_LEN)))
			{
				printf("Path traversal detected!\n");
				break;
			}

			/* Write the given data to a file */
			if ((fd = open(path, O_CREAT | O_RDWR, S_IRWXU)) < 0)
			{
				perror("Failed opening file");

				break;
			}

			if (write(fd, (uint8_t *)(packet + 1), len - sizeof(protocol_t)) <= 0)
			{
				perror("Error writing file");

				break;
			}

			close(fd);

			/* Check if this file is OK */
			snprintf(system_cmd, CMD_LEN + sizeof(CHECK_PROG) + 2, "%s %s", CHECK_PROG, path);

			/* Call checker */
			ret = system(system_cmd);

			if (ret != 0)
			{
				printf("Malicious file (%d).\n", ret);

				unlink(path);

				break;
			}
			
			break;
		}

		default:
		{
			/* Drop packet beacuse of unsupported control message. */
			printf("Unsupported control message.\n");

			break;
		}
	}
}

void handle_packet(uint8_t * packet, uint32_t len)
{
	/* Variable definition */
	protocol_t * header;

	/* Check that the packet is at least long enough to the protocol */
	if (len < sizeof(protocol_t))
	{
		/* Drop the packet */
		printf("Message received too short.\n");

		return;
	}

	/* Cast to the msg typedef */
	header = (protocol_t *)packet;

	/* Handle the message accordingly */
	switch (header->type)
	{
		case E_NORMAL:
		{
			if (header->control_type != E_CONTROL_NORMAL)
			{
				/* Drop packet because of invalid control message type. */
				printf("Invalid control message type.\n");

				return;
			}

			handle_normal_packet((uint8_t *)(header + 1), len);
			break;
		}

		case E_CONTROL:
		{
			handle_control_packet(header, len);
			break;
		}

		default:
		{
			printf("Unsupported packet type.\n");
			break;
		}
	}
}

#define DROP_PACKET(x) \
	do \
	{ \
		printf("Packet dropped: %s\n", x); \
	} \
	while (0)

uint32_t id_bitmap = 0;

frag_e collect_packets(uint8_t * pkt_buffer, uint32_t pkt_len, uint8_t ** o_full_packet, uint32_t * o_full_packet_size)
{
	/* Variable definition */
	uint32_t index;
	uint8_t * packet;
	collector_t * collector;
	hdr_t * pkt;
	struct timespec t;

	/* Code section */
	/* Get the packet */
	pkt = (hdr_t *)pkt_buffer;

	/* Check packet size */
	if (pkt_len != MAX_PACKET_SIZE + sizeof(hdr_t))
	{
		/* Drop packet. Too large. */
		DROP_PACKET("Too large");

		return E_ERR;
	}

	/* Accept only packets that are ID_WINDOW_SIZE IDs in the area of the last id received */
	if ((pkt->id - last_received_id > ID_WINDOW_SIZE) && (last_received_id - pkt->id > ID_WINDOW_SIZE))
	{
		/* Drop the packet if not in window */
		DROP_PACKET("Not in window");

		return E_ERR;
	}

	/* Check against replay attacks */
	if (id_bitmap & 1 << (ID_WINDOW_SIZE + last_received_id - pkt->id))
	{
		DROP_PACKET("Replayed packet");

		return E_ERR;
	}

	/* Get the relevant collector */
	for (index = 0; index < MAX_COLLECTORS; ++index)
	{
		if (collectors[index].id == pkt->id)
		{
			collector = &collectors[index];
			break;
		}
	}

	/* No relevant collector found */
	if (index == MAX_COLLECTORS)
	{
		/* Get an available collector */
		collector = &collectors[get_available_collector()];
	}

	/* Check if it is the first fragment received for this collector */
	if (collector->available)
	{
		/* Set all the primary arguments */
		collector->packet_size = pkt->size;
		collector->id = pkt->id;
		collector->total_fragments = collector->packet_size / MAX_PACKET_SIZE + !!(collector->packet_size % MAX_PACKET_SIZE);

		/* Add the fragment to the fragments list */
		collector->packets = malloc(collector->total_fragments * sizeof(hdr_t *));

		/* Collector is not available */
		collector->available = 0;
	}

	/* Make basic checks */
	/* Was the fragment already received? */
	if (collector->fragments_bitmap & (1 << pkt->frag_idx))
	{
		/* Fragment already exist */
		DROP_PACKET("Fragment alread exist");

		return E_ERR;

	}

	/* Check for valid fragment index */
	if (pkt->frag_idx >= collector->total_fragments)
	{
		/* Invalid fragment ID */
		DROP_PACKET("Invalid fragment ID");

		return E_ERR;

	}

	/* Check declared size of packet */
	if (pkt->size != collector->packet_size)
	{
		/* Invalid declared packet size */
		DROP_PACKET("Invalid declared packet size");

		return E_ERR;

	}

	/* No need to check for fragment size as all fragments are the same size */

	/* Set the fragment in the right place */
	collector->packets[collector->fragments] = pkt;

	/* Increase number of fragments */
	collector->fragments++;

	/* Update the bitmap */
	collector->fragments_bitmap |= 1 << pkt->frag_idx;

	/* Get the time */
	clock_gettime(CLOCK_REALTIME, &t);

	/* Set last update */
	collector->last_update = (uint32_t) ((t.tv_sec * 1000UL) + (t.tv_nsec / 1000000UL));

	if (collector->fragments == collector->total_fragments)
	{
		/* Check whether I should advance the last ID fields */
		if (
			((last_received_id < (uint32_t)-ID_WINDOW_SIZE) && (collector->id > last_received_id)) ||
			((last_received_id >= (uint32_t)-ID_WINDOW_SIZE) && ((collector->id < ID_WINDOW_SIZE) || collector->id > last_received_id))
		   )
		{
			/* Move the bitmap according to the id shift */
			id_bitmap <<= collector->id - last_received_id;

			last_received_id = collector->id;
		}

		/* Finally set this ID as received */
		id_bitmap |= 1 << (last_received_id - collector->id + ID_WINDOW_SIZE);

		/* Send the packet to reassembly */
		packet = build_packet(collector);

		printf("Finished packet: ID: %d Fragments: %d Size: %d Packet buffer: %p\n", collector->id, collector->total_fragments, collector->packet_size, packet);
		print_hex(packet, collector->packet_size);

		*o_full_packet = packet;
		*o_full_packet_size = collector->packet_size;

		/* Reset this collector */
		free_fragments(collector);

		return E_SUCCESS;
	}

	return E_FRAG;
}

#define PACKET_SIZE 1024
/* hdr_t ** break_packet(uint8_t * packet, uint32_t size, uint32_t src, uint32_t dst, uint32_t * o_frags) */
/* uint8_t * build_packet(collector_t * collector) */
/*
typedef struct collector_t
{
	hdr_t ** packets;
	uint32_t fragments;
	uint32_t total_fragments;
	uint32_t fragments_bitmap;
	uint32_t last_update;
	uint32_t packet_size;
	uint32_t id;
	uint8_t available;
} collector_t;
*/

/* #define MOCK_SEND */

int create_listening_socket(uint16_t port)
{
	/* Variable definition */
	int sockfd;
	struct sockaddr_in bind_addr;

	/* Code section */
	/* Create a socket for connection testing */
	sockfd = socket(AF_INET, SOCK_DGRAM, 0);

	/* Reset the addr struct */
	memset(&bind_addr, 0, sizeof(struct sockaddr_in));

	/* Fill it with appropriate data */
	bind_addr.sin_family = AF_INET;
	bind_addr.sin_port = htons(port);
	inet_aton("localhost", &bind_addr.sin_addr);

	/* Bind it to a network interface */
	if (bind(sockfd, (struct sockaddr *)&bind_addr, sizeof(struct sockaddr_in)) < 0)
	{
		/* Some error occured */
		perror("Error in binding socket");

		return 0;
	}

	return sockfd;
}


void init_collectors( void )
{
	uint32_t index;

	/* Init all the collectors */
	for (index = 0; index < MAX_COLLECTORS; ++index)
	{
		reset_collector(&collectors[index]);
	}
}

void moo_server( void )
{
	/* Variable definition */
	int sockfd;
	uint32_t index;
	uint32_t pkt_len;
	uint32_t addr_len;
	uint32_t full_packet_size;
	struct sockaddr_in addr;
	uint8_t * pkt;
	uint8_t * full_packet;
#ifdef MOCK_SEND
	uint8_t buf[PACKET_SIZE];
	ssize_t recvd_size;
	struct sockaddr_in recv_addr;
	socklen_t recv_addr_len;
#endif

	/* Code section */
	/* Create a socket for connection testing */
	if ((sockfd = create_listening_socket(0x2929)) == 0)
	{
		/* Something wrong happaned */
		return;
	}

	init_collectors();

	while (1)
	{
		/* Allocate receive buffer */
		pkt = malloc(MAX_PACKET_SIZE + sizeof(hdr_t));

		/* Set address len */
		addr_len = sizeof(struct sockaddr_in);

		/* Receive packet from network */
		pkt_len = recvfrom(sockfd, pkt, MAX_PACKET_SIZE + sizeof(hdr_t), 0, (struct sockaddr *)&addr, &addr_len);

		/* Call fragment receiving loop */
		if (collect_packets(pkt, pkt_len, &full_packet, &full_packet_size) == E_SUCCESS)
		{
			/* Forward to upper level handling of packet */
			handle_packet(full_packet, full_packet_size);

			free(full_packet);
		}
	}
#ifdef MOCK_SEND
	/* Set receive struct size */
	recv_addr_len = sizeof(struct sockaddr_in);

	/* Start receiving */
	recvd_size = recvfrom(sockfd, buf, PACKET_SIZE, 0, (struct sockaddr *)&recv_addr, &recv_addr_len);

	print_hex(buf, recvd_size);
#endif
	/* Close the socket */
	close(sockfd);
}

typedef struct
{
	char from_addr[3 * 4 + 3 + 1];
	char to_addr[3 * 4 + 3 + 1];
} mapping;
mapping address_mapping[] =
	{
		{

			"127.0.0.1",
			"127.0.0.1"
		}
	};

char * get_address_mapping(char * from)
{
	/* Variable definition */
	uint32_t i;

	/* Code section */
	for (i = 0; i < sizeof(address_mapping) / sizeof(mapping); ++i)
	{
		if (!strcmp(from, address_mapping[i].from_addr))
		{
			return address_mapping[i].to_addr;
		}
	}

	return 0;
}

/* #define MOCK_CLIENT */

void moo_client( void )
{
	/* Variable definition */
	uint32_t i;
#ifdef MOCK_CLIENT
	uint32_t c;
#endif
	uint32_t numfrags;
	uint8_t packet[PACKET_SIZE];
	uint8_t ** frags;

	/* Socket variable definition */
	int sockfd;
#ifndef MOCK_CLIENT
	int recv_sockfd;
	uint32_t recvd_size;
	uint32_t recv_addr_len;
	struct sockaddr_in recv_addr;
#endif
	struct sockaddr_in send_addr;

	/* Code section */
#ifndef MOCK_CLIENT
	/* Get a listening socket */
	if ((recv_sockfd = create_listening_socket(0x8394)) == 0)
	{
		/* Something wrong happaned */
		return;
	}

	/* Create a shortcut to tools directory */
	symlink("../tools", "tools");
#endif

	/* Create a socket for connection testing */
	sockfd = socket(AF_INET, SOCK_DGRAM, 0);

	/* Reset the addr struct */
	memset(&send_addr, 0, sizeof(struct sockaddr_in));

	/* Fill it with appropriate data */
	send_addr.sin_family = AF_INET;
	send_addr.sin_port = htons(0x2929);

#ifndef MOCK_CLIENT
	while (1)
	{
		/* Set receive struct size */
		recv_addr_len = sizeof(struct sockaddr_in);

		/* Start receiving */
		recvd_size = recvfrom(recv_sockfd, packet, PACKET_SIZE, 0, (struct sockaddr *)&recv_addr, &recv_addr_len);

		printf("Received packet with size: %d\n", recvd_size);

		/* Break the pakcet into fragments */
		frags = break_packet(packet, recvd_size, recv_addr.sin_addr.s_addr, 0/*get_address_mapping(recv_addr.sin_addr.s_addr)*/, &numfrags);

		/* Send the packet to it's rightful owner */
#ifndef MOCK_CLIENT
		inet_aton(get_address_mapping(inet_ntoa(recv_addr.sin_addr)), &send_addr.sin_addr);
#else
		inet_aton("localhost", &send_addr.sin_addr);
		printf("%d\n", send_addr.sin_addr.s_addr);
#endif

		/* Send the fragments one by one */
		for (i = 0; i < numfrags; ++i)
		{
			sendto(sockfd, frags[i], sizeof(hdr_t) + MAX_PACKET_SIZE, 0,
					(struct sockaddr *)&send_addr, sizeof(struct sockaddr_in));
		}
	}
#else
	/* Create the packet to send */
	for (i = 0; i < sizeof(packet); ++i)
	{
		packet[i] = 'a' + i % 26;
	}

	printf("Sending packet:\n");
	print_hex((uint8_t *)packet, sizeof(packet));

	for (c = 0; c < 50; ++c)
	{
		/* Break the pakcet into fragments */
		frags = break_packet(packet, sizeof(packet), 0x11223344, 0xAABBCCDD, &numfrags);

		/* printf("Number of frags: %d\n", numfrags); */

		/* Send the fragments one by one */
		for (i = 0; i < numfrags; ++i)
		{
			/* printf("Sending fragment #%d\n", i); */

			/* print_hex((uint8_t *)frags[i], sizeof(hdr_t) + MAX_PACKET_SIZE); */

			sendto(sockfd, frags[i], sizeof(hdr_t) + MAX_PACKET_SIZE, 0,
					(struct sockaddr *)&send_addr, sizeof(struct sockaddr_in));
		}
	}

	g_id = 1;

	/* Break the pakcet into fragments */
	frags = break_packet(packet, sizeof(packet), 0x11223344, 0xAABBCCDD, &numfrags);

	/* Send the fragments one by one */
	for (i = 0; i < numfrags; ++i)
	{
		sendto(sockfd, frags[i], sizeof(hdr_t) + MAX_PACKET_SIZE, 0,
				(struct sockaddr *)&send_addr, sizeof(struct sockaddr_in));
	}
#endif
	close(sockfd);
}
