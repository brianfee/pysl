#!/usr/bin/python

""" Main status line script. """

import os

def create_fifo(fifo):
    """ Create a first in, first out pipe. """
    os.mkfifo(fifo)

def main():
    """ Main function for pysl """
    print('pysl launched...')

    fifo = f'/tmp/pysl_input.{os.getpid()}'

    create_fifo(fifo)
    print(f'Pipe created at {fifo}')

if __name__ == '__main__':
    main()
