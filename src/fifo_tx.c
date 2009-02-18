/*
 * fifo_tx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "libfifo.h"

int main(int argc, char **argv)
{
	if (argc != 5)
	{
		printf("Usage: %s [pid] [dev] [host] [port]\n", argv[0]);
		exit(1);
	}

	char *pid = argv[1];
	char *dev = argv[2];
	char *host = argv[3];
	char *port = argv[4];

	int fifo = open_fifo_ro(pid, dev);
	void *fifo_data = map_memory(FIFO_WIDTH);
	ssize_t bytes_read = 0;

	int sock = open_udp_send_socket(host, port);
	ssize_t bytes_sent = 0;

	init_signals();

	while (NOT_KILLED)
	{
		bytes_read = read(fifo, fifo_data, FIFO_WIDTH);
		if (bytes_read == -1)
		{
			perror("read");
		}

		hexdump(fifo_data, FIFO_WIDTH);

		bytes_sent = send(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_sent == -1)
		{
			perror("send");
		}
	}

	close_file(fifo);
	unmap_memory(fifo_data, FIFO_WIDTH);
	close_file(sock);

	return 0;
}
