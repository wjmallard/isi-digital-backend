/*
 * fifo_rx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "fifo_rx.h"

#define FIFO_WIDTH 32

static unsigned char not_killed = 1;

int main(int argc, char **argv)
{
	if (argc != 3)
	{
		printf("Usage: %s [port] [file]\n", argv[0]);
		exit(1);
	}

	char *port = argv[1];
	char *path = argv[2];

	int sock = open_udp_recv_socket(port);
	void *fifo_data = map_memory(FIFO_WIDTH);
	ssize_t bytes_received = 0;

	int file = open_file_wo(path);
	ssize_t bytes_written = 0;

	//signal(SIGINT, cleanup);

	while (not_killed)
	{
		bytes_received = recv(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_received == -1)
		{
			perror("recv");
			exit(1);
		}

		hexdump(fifo_data, FIFO_WIDTH);

		bytes_written = write(file, fifo_data, FIFO_WIDTH);
		if (bytes_written == -1)
		{
			perror("write");
			exit(1);
		}
	}

	unmap_memory(fifo_data, FIFO_WIDTH);

	return 0;
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


void cleanup(int signal)
{
	printf("Ctrl-C caught! Quitting.\n");

	not_killed = 0;
}
