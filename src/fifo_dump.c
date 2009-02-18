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
	ssize_t bytes_read = 0;

	int file = open_file_wo(path);
	ssize_t bytes_written = 0;

	init_signals();

	while (NOT_KILLED)
	{
		bytes_read = read(fifo, fifo_data, FIFO_WIDTH);
		if (bytes_read == -1)
		{
			perror("read");
		}

		hexdump(fifo_data, FIFO_WIDTH);

		bytes_written = write(file, fifo_data, FIFO_WIDTH);
		if (bytes_written == -1)
		{
			perror("write");
		}
	}

	close_file(fifo);
	unmap_memory(fifo_data, FIFO_WIDTH);
	close_file(file);

	return 0;
}
