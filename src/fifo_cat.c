/*
 * fifo_cat.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 17-Feb-2008
 */

#include "libfifo.h"

#define FIFO_WIDTH 32

int main(int argc, char **argv)
{
	if (argc != 3)
	{
		printf("Usage: %s [pid] [dev]\n", argv[0]);
		exit(1);
	}

	char *pid = argv[1];
	char *dev = argv[2];

	int fifo = open_fifo_ro(pid, dev);
	void *fifo_data = map_memory(FIFO_WIDTH);
	ssize_t bytes_read = 0;

	//signal(SIGINT, cleanup);

	while (not_killed)
	{
		bytes_read = read(fifo, fifo_data, FIFO_WIDTH);
		if (bytes_read == -1)
		{
			perror("read");
			exit(1);
		}

		hexdump(fifo_data, FIFO_WIDTH);
	}

	unmap_memory(fifo_data, FIFO_WIDTH);

	return 0;
}
