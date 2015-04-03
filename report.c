#include "report.h"

static int create_socket(char * addr, uint16_t port)
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
	inet_aton(addr, &bind_addr.sin_addr);

	/* Bind it to a network interface */
	if (connect(sockfd, (struct sockaddr *)&bind_addr, sizeof(struct sockaddr_in)) < 0)
	{
		/* Some error occured */
		perror("Error in binding socket");

		return 0;
	}

	return sockfd;
}

#define MAX_PKT_SIZE 1024

void ReportBug(char * ip, uint16_t port, const char * func_name)
{
	int sock;
	int len = strlen(func_name);
	char pkt[MAX_PKT_SIZE];

	sock = create_socket(ip, port);

	memcpy(pkt, &len, sizeof(len));
	memcpy(pkt + sizeof(len), func_name, len);

	send(sock, pkt, sizeof(len) + len, 0);
	printf("Report sent.\n");

	close(sock);	
}
