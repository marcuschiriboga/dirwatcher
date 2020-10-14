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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

"""this lets me store what I have already looked at in memory,"""
"""so I wont need to re-read sections of files I have already read."""
memory_log = {}


def search_for_magic(filename, start_line, magic_string, path):
    """look through files one line at a time for the magic phrase."""
    """on match, log"""
    try:
        with open(os.path.join(path, filename)) as f:
            lines = f.readlines()
            for line in range(len(lines)):
                if line > start_line:
                    if magic_string in lines[line]:
                        memory_log[filename].add(line)
                        logger.info("match: " + path + filename +
                                    " at line " + str(line+1))
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


def watch_directory(path, magic_string, extension):
    """arrange the other functions to set the memory-log up before reading"""
    """send exception for errors"""
    try:
        files = os.listdir(path)
        # if not files:
        #     logger.info(f"the directory at {path} is empty")
        if files != list(memory_log.keys()):
            """if files is different from the memory"""
            detect_new_files(files),
            detect_removed_files(files),
        for item in files:
            """look at each file, starting where we left off"""
            if extension == os.path.splitext(item)[1]:
                search_for_magic(
                    item, max(memory_log[item]), magic_string, path)
    except FileNotFoundError:
        logger.info(f"directory not found at {path}")
    except KeyError:
        logger.info("key error")
    return


def create_parser():
    """Creates an argument parser object."""
    """ to watch(dir), file extension to filter on(ext),
    polling interval(int) and magic text(magic)"""
    parser = argparse.ArgumentParser()
    parser.add_argument('dir',
                        help='destination directory to look for files')
    parser.add_argument('magic',
                        help='a search phrase')
    parser.add_argument("-e", '--extension', default=".txt",
                        help='file extrension to filter on')
    parser.add_argument('-i', '--interval', default="1",
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
        logger.info(f"exited from signal {signal.Signals(signum).name}")
        return


def main(args):
    parser = create_parser()
    looper = signal_handler()
    if not args:
        parser.print_usage()
        """program asks for no sys.exit(1),
        I assume they ment in context of signal handlers"""
        sys.exit(1)
    parsed_args = parser.parse_args(args)
    magic_phrase = parsed_args.magic
    start_time = time.time()
    logger.info(
        f"starting dirwatcher.py for {magic_phrase} in {parsed_args.dir}")
    while not looper.kill_now:
        time.sleep(int(parsed_args.interval))
        watch_directory(parsed_args.dir, magic_phrase,
                        parsed_args.extension)
    end_time = time.time()
    logger.info("dirwatcher.py stopped. it ran for: " +
                str(int(end_time - start_time))+" seconds")
    return


if __name__ == '__main__':
    main(sys.argv[1:])
