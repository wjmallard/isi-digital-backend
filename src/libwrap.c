/*
 * libnet.c
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#include "libwrap.h"

int Socket(int domain, int type, int protocol)
{
	int sock;

	sock = socket(AF_INET, SOCK_DGRAM, 0);
	if (sock == -1)
	{
		perror("socket");
		exit(1);
	}

	return sock;
}

int Bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen)
{
	int status;

	status = bind(sockfd, addr, addrlen);
	if (status == -1)
	{
		perror("bind");
		exit(1);
	}

	return status;
}

int Connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen)
{
	int status;

	status = connect(sockfd, addr, addrlen);
	if (status == -1)
	{
		perror("connect");
		exit(1);
	}

	return status;
}

ssize_t Send(int socket, const void *buffer, size_t length, int flags)
{
	ssize_t bytes_sent;

	bytes_sent = send(socket, buffer, length, flags);
	if (bytes_sent == -1)
	{
		perror("send");
		if (errno != EINTR)
		{
			exit(1);
		}
	}

	return bytes_sent;
}

ssize_t Recv(int socket, void *buffer, size_t length, int flags)
{
	ssize_t bytes_received;

	bytes_received = recv(socket, buffer, length, flags);
	if (bytes_received == -1)
	{
		perror("recv");
		if (errno != EINTR)
		{
			exit(1);
		}
	}

	return bytes_received;
}

ssize_t Write(int fildes, const void *buf, size_t nbyte)
{
	ssize_t bytes_written;

	bytes_written = write(fildes, buf, nbyte);
	if (bytes_written == -1)
	{
		perror("write");
		if (errno != EINTR)
		{
			exit(1);
		}
	}

	return bytes_written;
}

ssize_t Read(int fildes, void *buf, size_t nbyte)
{
	ssize_t bytes_read;

	bytes_read = read(fildes, buf, nbyte);
	if (bytes_read == -1)
	{
		perror("read");
		if (errno != EINTR)
		{
			exit(1);
		}
	}

	return bytes_read;
}
