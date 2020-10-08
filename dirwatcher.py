#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "marcus"

import sys
import argparse
import os
import signal
import time
import logging

logging.basicConfig(filename='example.log',
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

"""this lets me store what I have already looked at in memory,"""
"""I wont need to re-read sections of files I have already read."""
memory_log = {}


def search_for_magic(filename, start_line, magic_string, path):
    """look through files one line at a time for the magic phrase."""
    """on match, log"""
    try:
        with open(path + filename) as f:
            lines = f.readlines()
            match = False
            if start_line:
                match = True
            for line in range(len(lines)):
                if line > start_line:
                    if magic_string in lines[line]:
                        match = True
                        if filename not in memory_log.keys():
                            memory_log.update({filename: {line}})
                            logger.info("match: " + path + filename +
                                        " at line " + str(line))
                        else:
                            memory_log[filename].add(line)
                            logger.info("match: " + path + filename +
                                        " at line " + str(line))
            if match:
                # if I need to clear out -1 from the log memory
                pass
    except FileNotFoundError:
        logger.info("file not found")
    except IsADirectoryError:
        logger.info("this is a directory not a file error")
    return


def detect_new_files(files):
    # compare the new loop with the state for changes
    for file in files:
        if file not in list(memory_log.keys()):
            logger.info(f'{file} added')
            memory_log.update({file: {-1}})
    return


def detect_removed_files(files):
    # compare the state with the new loop for changes
    for _ in list(memory_log.keys()):
        if _ not in files:
            logger.info(f'{_} removed')
            memory_log.pop(_)
    return


def watch_directory(path, magic_string, extension, interval):
    """arrange the other functions to set the memory-log up before reading"""
    """send exception for errors"""
    try:
        files = os.listdir(path)

        if files != list(memory_log.keys()):
            """if files is different from the memory"""
            logger.info("file change or start up")
            detect_new_files(files),
            detect_removed_files(files),
        if not memory_log:
            """prevent key errors"""
            for item in files:
                search_for_magic(item, 0, magic_string, path)
        else:
            for item in files:
                """look at each file, starting where we left off"""
                search_for_magic(
                    item, max(memory_log[item]), magic_string, path)
    except FileNotFoundError:
        logger.info("--nothing is there--\n--did you make typo?--")
    except KeyError:
        logger.info("key error")
    return


def create_parser():
    """Creates an argument parser object."""
    """ to watch(dir), file extension to filter on(ext),
    polling interval(int) and magic text(magic)"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', '--directory',
                        help='destination directory to look for files')
    parser.add_argument("-ext", '--extension',
                        help='file extrension to filter on')
    parser.add_argument('-maj', '--magic',
                        help='a search phrase')
    parser.add_argument('-int', '--interval',
                        help="polling interval")
    return parser


class signal_handler:
    """ this signal handler was taken from google as a easy to implement
    solution """
    """it interprets system info to modify functionallity, close"""
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        print("bye bye")
        logger.info("exited from signal")
        return


def main(args):
    parser = create_parser()
    looper = signal_handler()
    if not args:
        parser.print_usage()
        sys.exit(1)
    parsed_args = parser.parse_args(args)
    magic_phrase = parsed_args.magic
    logger.info("start up")
    print("running, check the log for more info")
    while not looper.kill_now:
        time.sleep(int(parsed_args.interval))
        watch_directory(parsed_args.directory, magic_phrase,
                        parsed_args.extension, parsed_args.interval)
    return


if __name__ == '__main__':
    main(sys.argv[1:])
