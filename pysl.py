#!/usr/bin/python

""" Main status line script. """

import argparse
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time

FIFO = '/tmp/pysl'
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

def start_watcher():
    """ Daemon process for watching input pipe. """
    global OUTPUT # pylint: disable=global-statement

    while True:
        data = read_fifo(FIFO)
        OUTPUT.append(data)
        OUTPUT_AVAILABLE.set()

def get_command_output(cmd):
    """ Run an OS command, and return the stdout. """
    result = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE,
                            check=True)
    return result.stdout.decode('utf-8')

def parse_arguments():
    """ Parses command line arguments. """
    desc = """Python Status Line"""
    parser = argparse.ArgumentParser(description=desc)

    # Positional Arguments
    parser.add_argument('text', type=str, default='', nargs='?')

    # Optional Arguments
    parser.add_argument('-d', '--delay', type=float, metavar='N', default=3,
                        help="""seconds to wait for messages before
                            default action (default: 3s)""")
    parser.add_argument('-i', '--id', type=str, metavar='ID',
                        help='specify id (default: process id')
    parser.add_argument('-t', '--timer', type=float, metavar='N', default=0.3,
                        help='seconds to display messages (default: 0.3s)')
    parser.add_argument('-w', '--watch', help='run program in watcher mode',
                        action='store_true')
    parser.add_argument('--default-cmd', type=str, metavar='CMD', dest='cmd',
                        help='command to run when no messages are queued')

    return parser.parse_args()

def main():
    """ Main function for pysl """
    args = parse_arguments()

    global FIFO # pylint: disable=global-statement
    if args.id:
        FIFO += f'.{args.id}'

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
                OUTPUT_AVAILABLE.wait(args.delay)

            OUTPUT_AVAILABLE.clear()

            # Check for any additions to output, avoiding race condition.
            if not OUTPUT:
                OUTPUT.append(get_command_output(args.cmd) if args.cmd else '')

            print(OUTPUT.pop(0), end='')
            time.sleep(args.timer)
            sys.stdout.flush()

    else:
        pipes = [FIFO] if args.id else get_fifo_list()

        for pipe in pipes:
            write_fifo(pipe, args.text)

if __name__ == '__main__':
    main()
