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
	int sock = open_udp_send_socket(host, port);

	init_signals();

	while (NOT_KILLED)
	{
		Read(fifo, fifo_data, FIFO_WIDTH);
		Send(sock, fifo_data, FIFO_WIDTH, 0);
	}

	close_file(fifo);
	unmap_memory(fifo_data, FIFO_WIDTH);
	close_file(sock);

	return 0;
}
