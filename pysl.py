#!/usr/bin/python

""" Main status line script. """

import os

def create_fifo():
    pid = os.getpid()
    fifo = f'/tmp/pysl_input.{pid}'
    os.mkfifo(fifo)
    return fifo

def main():
    """ Main function for pysl """
    print('pysl launched...')
    print(f'Pipe created at {create_fifo()}')

if __name__ == '__main__':
    main()
