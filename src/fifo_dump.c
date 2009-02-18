/*
 * fifo_dump.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 17-Feb-2008
 */

#include "libfifo.h"

int main(int argc, char **argv)
{
	if (argc != 4)
	{
		printf("Usage: %s [pid] [dev] [file]\n", argv[0]);
		exit(1);
	}

	char *pid = argv[1];
	char *dev = argv[2];
	char *path = argv[3];

	int fifo = open_fifo_ro(pid, dev);
	void *fifo_data = map_memory(FIFO_WIDTH);
	int file = open_file_wo(path);

	init_signals();

	while (NOT_KILLED)
	{
		Read(fifo, fifo_data, FIFO_WIDTH);
		hexdump(fifo_data, FIFO_WIDTH);
		Write(file, fifo_data, FIFO_WIDTH);
	}

	close_file(fifo);
	unmap_memory(fifo_data, FIFO_WIDTH);
	close_file(file);

	return 0;
}
