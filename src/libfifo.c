/*
 * libnet.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "libfifo.h"

#define BUFFER_LENGTH 128

/*
 * Open a UDP connection to the specified host.
 */
int open_udp_send_socket(char *dst_host, char *dst_port)
{
	struct sockaddr_in dst_addr;
	memset(&dst_addr, 0, sizeof(struct sockaddr_in));
	dst_addr.sin_family = AF_INET;
	dst_addr.sin_addr.s_addr = parse_host(dst_host);
	dst_addr.sin_port = parse_port(dst_port);

	int sock = socket(AF_INET, SOCK_DGRAM, 0);

	int status = connect(sock, (struct sockaddr *)&dst_addr, sizeof(dst_addr));
	if (status == -1)
	{
		printf("Cannot open connection to %s on port %s.\n", dst_host, dst_port);
		perror("connect");
	}

	return sock;
}

/*
 * Open a UDP connection on the specified port.
 */
int open_udp_recv_socket(char *dst_port)
{
	struct sockaddr_in src_addr;
	memset(&src_addr, 0, sizeof(struct sockaddr_in));
	src_addr.sin_family = AF_INET;
	src_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	src_addr.sin_port = parse_port(dst_port);

	int sock = socket(AF_INET, SOCK_DGRAM, 0);

	bind(sock, (struct sockaddr *)&src_addr, sizeof(src_addr));

	return sock;
}

/*
 * Parse an address string into an address structure.
 */
unsigned long int parse_host(char *host_str)
{
	struct in_addr host;
	struct hostent *he;

	he = gethostbyname(host_str);
	if (he == NULL)
	{
		printf("Cannot find host %s.\n", host_str);
		perror("gethostbyname");
		exit(1);
	}
	host = *((struct in_addr *)he->h_addr);

	return host.s_addr;
}

/*
 * Parse a port string into a port number.
 */
unsigned short int parse_port(char *port_str)
{
	short unsigned int port = 0;
	sscanf(port_str, "%hu", &port);
	return htons(port);
}

/*
 * Open a file for reading.
 */
int open_file_ro(char *path)
{
	int fifo_fd = -1;

	int flags = O_RDONLY;

	fifo_fd = open(path, flags);
	if (fifo_fd == -1)
	{
		perror("open");
		exit(1);
	}

	return fifo_fd;
}

/*
 * Open a file for writing.
 */
int open_file_wo(char *path)
{
	int file_fd = -1;

	int flags = O_WRONLY|O_CREAT|O_TRUNC;
	mode_t mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH;

	file_fd = open(path, flags, mode);
	if (file_fd == -1)
	{
		perror("open");
		exit(1);
	}

	return file_fd;
}

/*
 * Open a fifo for reading.
 */
int open_fifo_ro(char *pid, char *dev)
{
	int fifo_fd = -1;

	char fifo_path[BUFFER_LENGTH];
	memset(&fifo_path, 0, sizeof(fifo_path));
	snprintf(fifo_path, BUFFER_LENGTH, "/proc/%s/hw/ioreg/%s", pid, dev);

	fifo_fd = open_file_ro(fifo_path);

	return fifo_fd;
}

/*
 * Print the contents of a raw memory chunk.
 */
void hexdump(void *data, int size)
{
	printf("data:");

	int i;
	for (i=0; i<size; i++)
	{
		if (i%4 == 0)
		{
			printf(" ");
		}
		printf("%02X", *(unsigned char *)(data + i));
	}

	printf("\n");
}

/*
 * Allocate some fast memory.
 */
void *map_memory(size_t size)
{
	void *memory = NULL;

	void *addr = NULL;
	size_t len = size;
	int prot = PROT_READ|PROT_WRITE;
	int flags = MAP_PRIVATE|MAP_ANONYMOUS;
	int fd = -1;
	off_t off = 0;

	memory = mmap(addr, len, prot, flags, fd, off);
	if (memory == MAP_FAILED)
	{
		perror("mmap");
		exit(1);
	}

	return memory;
}

/*
 * Deallocate some fast memory.
 */
void unmap_memory(void *addr, size_t size)
{
	int status = 0;

	status = munmap(addr, size);
	if (status == -1)
	{
		perror("munmap");
		exit(1);
	}
}

void cleanup(int signal)
{
	printf("Ctrl-C caught! Quitting.\n");

	not_killed = 0;
}
