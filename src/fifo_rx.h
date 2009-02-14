/*
 * fifo_rx.h
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#ifndef FIFO_RX_H_
#define FIFO_RX_H_

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

#include "libnet.h"

int open_file_wo(char *path);

#endif /* FIFO_RX_H_ */
