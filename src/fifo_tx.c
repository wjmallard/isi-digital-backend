/*
 * fifo_tx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "fifo_tx.h"

#define FIFO_WIDTH 32
#define BUFFER_LENGTH 128

static unsigned char not_killed = 1;

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

	signal(SIGINT, cleanup);

	while (not_killed)
	{
		bytes_read = read(fifo, fifo_data, FIFO_WIDTH);
		if (bytes_read == -1)
		{
			perror("read");
			exit(1);
		}

		hexdump(fifo_data, FIFO_WIDTH);

		bytes_sent = send(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_sent == -1)
		{
			perror("send");
			exit(1);
		}
	}

	unmap_memory(fifo_data, FIFO_WIDTH);

	return 0;
}

/*
 * Open a fifo for reading.
 */
int open_fifo_ro(char *pid, char *dev)
{
	int fifo_fd = -1;

	int flags = O_RDONLY;
	char fifo_path[BUFFER_LENGTH];
	memset(&fifo_path, 0, sizeof(fifo_path));
	snprintf(fifo_path, BUFFER_LENGTH, "/proc/%s/hw/ioreg/%s", pid, dev);

	fifo_fd = open(fifo_path, flags);
	if (fifo_fd == -1)
	{
		perror("open");
		exit(1);
	}

	return fifo_fd;
}

void cleanup(int signal)
{
	printf("Ctrl-C caught! Quitting.\n");

	not_killed = 0;
}
