/*
 * fifo_tx.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "fifo_tx.h"

#define BYTE 1
#define FIFO_WIDTH 32
#define BUFFER_LENGTH 128

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
	void *fifo_data = calloc(FIFO_WIDTH, BYTE);
	ssize_t bytes_read = 0;

	int sock = open_udp_send_socket(host, port);
	ssize_t bytes_sent = 0;

	while (bytes_read >= 0)
	{
		bytes_read = read(fifo, fifo_data, FIFO_WIDTH);
		if (bytes_read == -1)
		{
			perror("read");
		}

		printf("Read %d bytes.\n", (int)bytes_read);
		hexdump(fifo_data, FIFO_WIDTH);

		bytes_sent = send(sock, fifo_data, FIFO_WIDTH, 0);
		if (bytes_sent == -1)
		{
			perror("send");
		}

		printf("Sent %d bytes.\n", (int)bytes_sent);

		break;
	}

	return 0;
}

/*
 * Open a fifo for reading.
 */
int open_fifo_ro(char *pid, char *dev)
{
	int flags = O_RDONLY;
	char *fifo_path = (char *)calloc(BUFFER_LENGTH, BYTE);
	snprintf(fifo_path, BUFFER_LENGTH, "/proc/%s/hw/ioreg/%s", pid, dev);

	int fifo_fd = open(fifo_path, flags);
	if (fifo_fd == -1)
	{
		perror("open");
		return -1;
	}

	return fifo_fd;
}
