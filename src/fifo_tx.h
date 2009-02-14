/*
 * fifo_tx.h
 *
 * auth: Billy Mallard
 * mail: wjm@berkeley.edu
 * date: 13-Feb-2008
 */

#ifndef FIFO_TX_H_
#define FIFO_TX_H_

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

#include "libnet.h"

int open_fifo_ro(char *pid, char *dev);

#endif /* FIFO_TX_H_ */
