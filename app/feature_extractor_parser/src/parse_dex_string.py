#!/usr/bin/env python

import sys
import logging
import pprint

infile = sys.argv[1]


def filter(string):
    if len(string) < 3:
        return None
    return string


if __name__ == "__main__":
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.WARNING)
    channel = logging.StreamHandler()
    channel.setLevel(logging.WARNING)
    logger.addHandler(channel)

    with open(infile, "rb") as f:
        strings = [x.strip() for x in f.read().split(b'\0') if x != b'' if x != b'']
        pprint.pprint(strings)
