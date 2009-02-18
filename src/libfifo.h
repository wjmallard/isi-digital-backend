/*
 * libnet.h
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#ifndef _LIBNET_H_
#define _LIBNET_H_

#include <fcntl.h>
#include <netdb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

static unsigned char not_killed = 1;

int open_udp_send_socket(char *dst_host, char *dst_port);
int open_udp_recv_socket(char *dst_port);
unsigned long int parse_host(char *host_name);
unsigned short int parse_port(char *port_str);

int open_file_ro(char *path);
int open_file_wo(char *path);
int open_fifo_ro(char *pid, char *dev);

void hexdump(void *data, int size);
void *map_memory(size_t size);
void unmap_memory(void *addr, size_t size);

void cleanup(int signal);

#endif /* _LIBNET_H_ */
