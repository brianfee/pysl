#!/usr/bin/python

""" Main status line script. """

import os
import signal
import sys

FIFO = f'/tmp/pysl.{os.getpid()}'

def signal_handler(sig, frame):
    delete_fifo(FIFO)
    sys.exit(0)

def create_fifo(fifo):
    """ Create a FIFO pipe. """
    os.mkfifo(fifo)

def read_fifo(fifo):
    """ Open and read input from a FIFO pipe. """
    with open(fifo) as pipe:
        while True:
            data = pipe.read()

            if len(data) == 0:
                break;

            print(data, end='')

def delete_fifo(fifo):
    """ Delete a FIFO pipe. """
    os.remove(fifo)

def main():
    """ Main function for pysl """
    print('pysl launched...')
    create_fifo(FIFO)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        read_fifo(FIFO)

if __name__ == '__main__':
    main()
