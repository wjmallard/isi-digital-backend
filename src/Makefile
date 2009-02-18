CC=gcc
CFLAGS=-g -Wall
SOFLAGS=-c -fPIC

all: fifo_tx fifo_rx fifo_cat fifo_dump

libfifo.o: libfifo.c libfifo.h
	$(CC) $(CFLAGS) $(SOFLAGS) libfifo.c -o libfifo.o 

libwrap.o: libwrap.c libwrap.h
	$(CC) $(CFLAGS) $(SOFLAGS) libwrap.c -o libwrap.o 

fifo_tx: fifo_tx.c libfifo.o libwrap.o
	$(CC) $(CFLAGS) fifo_tx.c libfifo.c libwrap.c -o fifo_tx

fifo_rx: fifo_rx.c libfifo.o libwrap.o
	$(CC) $(CFLAGS) fifo_rx.c libfifo.c libwrap.c -o fifo_rx

fifo_cat: fifo_cat.c libfifo.o libwrap.o
	$(CC) $(CFLAGS) fifo_cat.c libfifo.c libwrap.c -o fifo_cat

fifo_dump: fifo_dump.c libfifo.o libwrap.o
	$(CC) $(CFLAGS) fifo_dump.c libfifo.c libwrap.c -o fifo_dump

clean:
	@rm -vf *.o
	@rm -vf *~
	@rm -vf fifo_tx
	@rm -vf fifo_rx
	@rm -vf fifo_cat
	@rm -vf fifo_dump
