#!/usr/bin/python

""" Main status line script. """

import argparse
import os
import signal
import sys

FIFO = f'/tmp/pysl.{os.getpid()}'

def cleanup(sig, frame): # pylint: disable=unused-argument
    """ Cleanup on OS signals. """
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
                break

            print(data, end='')

def write_fifo(fifo, output):
    """ Open and append output to a FIFO pipe. """
    print(fifo)
    with open(fifo, 'w') as pipe:
        pipe.write(output + '\n')
        pipe.flush()

def delete_fifo(fifo):
    """ Delete a FIFO pipe. """
    os.remove(fifo)

def parse_arguments():
    """ Parses command line arguments. """
    desc = """Python Status Line"""
    parser = argparse.ArgumentParser(description=desc)

    # Positional Arguments
    parser.add_argument('text', type=str, default='', nargs='?')

    # Optional Arguments
    parser.add_argument('-p', '--pid', help='specify process id', type=str,
                        metavar='PID')
    parser.add_argument('-w', '--watch', help='run program in watcher mode.',
                        action='store_true')

    return parser.parse_args()


def main():
    """ Main function for pysl """

    args = parse_arguments()

    print(args.pid)
    print(args.text)
    if not args.watch:
        write_fifo(f'/tmp/pysl.{args.pid}', args.text)
        sys.exit()

    print('pysl launched...')
    sys.stdout.flush()
    create_fifo(FIFO)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGHUP, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        read_fifo(FIFO)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
