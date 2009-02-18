/*
 * fifo_rx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "libfifo.h"

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

	init_signals();

	while (NOT_KILLED)
	{
		recv(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_received == -1)
		{
			perror("recv");
		}

		hexdump(fifo_data, FIFO_WIDTH);

		bytes_written = write(file, fifo_data, FIFO_WIDTH);
		if (bytes_written == -1)
		{
			perror("write");
		}
	}

	close_file(sock);
	unmap_memory(fifo_data, FIFO_WIDTH);
	close_file(file);

	return 0;
}
