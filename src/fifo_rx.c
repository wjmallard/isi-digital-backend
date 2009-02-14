/*
 * fifo_rx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "fifo_rx.h"

#define BYTE 1
#define FIFO_WIDTH 32

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
	void *fifo_data = calloc(FIFO_WIDTH, BYTE);
	ssize_t bytes_received = 0;

	int file = open_file_wo(path);
	ssize_t bytes_written = 0;

	while (bytes_received >= 0)
	{
		bytes_received = recv(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_received == -1)
		{
			perror("recv");
		}

		printf("Received %d bytes.\n", (int)bytes_received);
		hexdump(fifo_data, FIFO_WIDTH);

		bytes_written = write(file, fifo_data, FIFO_WIDTH);
		if (bytes_written == -1)
		{
			perror("write");
		}

		printf("Wrote %d bytes.\n", (int)bytes_written);

		break;
	}

	return 0;
}

/*
 * Open a file for writing.
 */
int open_file_wo(char *path)
{
	int flags = O_WRONLY|O_CREAT|O_TRUNC;
	mode_t mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH;

	int file_fd = open(path, flags, mode);
	if (file_fd == -1)
	{
		perror("open");
		exit(-1);
	}
	return file_fd;
}
