#!/usr/bin/env python

import sys
import logging


infile = sys.argv[1]


def read_until_parentheses(f):
    buf = b""
    ch = f.read(1)
    buf = ch

    while ch:
        if ch == b")":
            buf += ch
            return buf
        else:
            buf += ch
        ch = f.read(1)
    sys.exit(1)


if __name__ == "__main__":
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.WARNING)
    channel = logging.StreamHandler()
    channel.setLevel(logging.WARNING)
    logger.addHandler(channel)

    with open(infile, "rb") as f:

        id = f.read(2)
        while id != b"":
            logger.info("id = %s" % id.hex())

            method = read_until_parentheses(f)
            logger.info("method = %s" % method)

            opcode_len = int.from_bytes(f.read(2), byteorder='little', signed=False)        # XXX FIXME: verify with Tibor
            logger.info("opcode_len = %d" % opcode_len)

            try:
                opcodes = f.read(opcode_len)
                # logger.info("opcodes (hex): %s" % opcodes.hex(' ', 4))                # only works with python 3.8
                logger.info("opcodes (hex): %s" % opcodes.hex())
            except Exception as ex:
                print("could not read opcodes, error %s. Quitting." % str(ex))
                sys.exit(2)
            print('%s,"%s",%d,%s' %(id.hex(), method.decode('utf-8', errors="ignore"), opcode_len, opcodes.hex()))
            id = f.read(2)
