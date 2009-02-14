all: fifo_tx fifo_rx

fifo_tx: fifo_tx.c libnet.o
	gcc -g -Wall fifo_tx.c libnet.c -o fifo_tx

fifo_rx: fifo_rx.c libnet.o
	gcc -g -Wall fifo_rx.c libnet.c -o fifo_rx

clean:
	@rm -vf *.o
	@rm -vf *~
	@rm -vf fifo_tx
	@rm -vf fifo_rx
