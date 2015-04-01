#ifndef __REPORT_H__
#define __REPORT_H__

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

void ReportBug(char * ip, uint16_t port, const char * func_name);

#define REPORT(ip, port) ReportBug((ip), (port), __FUNCTION__)

#endif
