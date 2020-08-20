#!/usr/bin/python

""" Main status line script. """

import argparse
import os
import re
import signal
import sys
import threading
import time

FIFO = f'/tmp/pysl.{os.getpid()}'
OUTPUT = []
OUTPUT_AVAILABLE = threading.Event()

def cleanup(sig, frame): # pylint: disable=unused-argument
    """ Cleanup on OS signals. """
    delete_fifo(FIFO)

    print("Process interrupt detected. Exiting...")
    sys.exit(0)

def get_fifo_list():
    """ Get list of active FIFOs created by pysl processes. """
    rootdir = '/tmp'

    pipes = []
    for root, _, files in os.walk(rootdir):
        for f in files: # pylint: disable=invalid-name
            if re.search('pysl.?', f):
                pipes.append(f'{root}/{f}')

    return pipes

def create_fifo(fifo):
    """ Create a FIFO pipe. """
    os.mkfifo(fifo)

def read_fifo(fifo):
    """ Open and read input from a FIFO pipe. """
    ret_data = ''

    with open(fifo) as pipe:
        while True:
            data = pipe.read()

            if len(data) == 0:
                break

            ret_data = data

    return ret_data

def write_fifo(fifo, output):
    """ Open and append output to a FIFO pipe. """
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

def start_watcher():
    """ Daemon process for watching input pipe. """
    global OUTPUT # pylint: disable=global-statement

    while True:
        data = read_fifo(FIFO)
        OUTPUT.append(data)
        OUTPUT_AVAILABLE.set()


def main():
    """ Main function for pysl """
    args = parse_arguments()

    if args.watch:
        print('pysl launched...')
        sys.stdout.flush()
        create_fifo(FIFO)

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGHUP, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        watcher = threading.Thread(target=start_watcher, daemon=True)
        watcher.start()

        while True:
            if not OUTPUT:
                OUTPUT_AVAILABLE.wait()

            OUTPUT_AVAILABLE.clear()
            print(OUTPUT.pop(0), end='')
            time.sleep(1)
            sys.stdout.flush()

    else:
        pipes = [f'/tmp/pysl.{args.pid}'] if args.pid else get_fifo_list()

        for pipe in pipes:
            write_fifo(pipe, args.text)

if __name__ == '__main__':
    main()
