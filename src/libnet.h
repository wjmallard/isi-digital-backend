/*
 * libnet.h
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#ifndef LIBNET_H_
#define LIBNET_H_

#include <fcntl.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int open_udp_send_socket(char *dst_host, char *dst_port);
int open_udp_recv_socket(char *dst_port);
unsigned long int parse_host(char *host_name);
unsigned short int parse_port(char *port_str);
void hexdump(void *data, int size);

#endif /* LIBNET_H_ */
