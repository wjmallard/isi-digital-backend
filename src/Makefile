CC=gcc
CFLAGS=-g -Wall
SOFLAGS=-c -fPIC -shared
SOLIBS=-L. -lfifo -lwrap

all: fifo_tx fifo_rx fifo_cat fifo_dump

libs: libfifo.so libwrap.so

libfifo.so: libfifo.c libfifo.h
	$(CC) $(CFLAGS) $(SOFLAGS) libfifo.c -o libfifo.so 

libwrap.so: libwrap.c libwrap.h
	$(CC) $(CFLAGS) $(SOFLAGS) libwrap.c -o libwrap.so 

fifo_tx: fifo_tx.c libs
	$(CC) $(CFLAGS) fifo_tx.c -o fifo_tx $(SOLIBS)

fifo_rx: fifo_rx.c libs
	$(CC) $(CFLAGS) fifo_rx.c -o fifo_rx $(SOLIBS)

fifo_cat: fifo_cat.c libs
	$(CC) $(CFLAGS) fifo_cat.c -o fifo_cat $(SOLIBS)

fifo_dump: fifo_dump.c
	$(CC) $(CFLAGS) fifo_dump.c -o fifo_dump $(SOLIBS)

clean:
	@rm -vf *.o
	@rm -vf *.so
	@rm -vf *~
	@rm -vf fifo_tx
	@rm -vf fifo_rx
	@rm -vf fifo_cat
	@rm -vf fifo_dump
