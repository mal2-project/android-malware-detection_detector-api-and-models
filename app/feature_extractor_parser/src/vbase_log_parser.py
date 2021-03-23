#!/usr/bin/env python

import os
import sys
import re
import logging

path = sys.argv[1]


regexp = re.compile('^([0-9]+\.blk).*\) Sig: ([A-Z_]+) \(.*$')


""" input format of the .log file:

0000.blk : Scan 0x00000000 - 0x000001ee (0 - 494) Sig: SIGNUM_ANDROID_MF (0x00000056) "APK:Android manifest"
0001.blk : Scan 0x00000000 - 0x00000267 (0 - 615) Sig: SIGNUM_ANDROID_MF (0x00000056) "APK:Android/Java security file"
0002.blk : Scan 0x00000000 - 0x0000042f (0 - 1071) Sig: SIGNUM_ANDROID_XML (0x00000068) "APK:AXML:AndroidManifest.XML"
0003.blk : Scan 0x00000000 - 0x00014d22 (0 - 85282) Sig: SIGNUM_DEX_STRING (0x0000004d) "APK:DEX:DEX strings"
0004.blk : Scan 0x00000000 - 0x000027e8 (0 - 10216) Sig: SIGNUM_DEX_OPCODE_NORMALIZED (0x00000051) "APK:DEX:DEX opcodes normalized"
0005.blk : Scan 0x00000000 - 0x00027318 (0 - 160536) Sig: SIGNUM_DEX_OPCODE_LIBRARY (0x00000071) "APK:DEX:DEX library opcodes normalized"
0006.blk : Scan 0x00000000 - 0x000000a1 (0 - 161) Sig: SIGNUM_DEX_ARRAYS (0x00000063) "APK:DEX:DEX Arrays data"
0007.blk : Scan 0x00000000 - 0x00000c03 (0 - 3075) Sig: SIGNUM_ARSC (0x00000046) "APK:Flat:Android Resource File"
0008.blk : Scan 0x00000000 - 0x0000071d (0 - 1821) Sig: SIGNUM_CERT (0x00000057) "APK:Flat:Certificate"
0009.blk : Scan 0x00000000 - 0x00008a53 (0 - 35411) Sig: SIGNUM_PNG_FILE (0x00000035) "APK:Flat:PNG File"
0010.blk : Scan 0x00000000 - 0x00000022 (0 - 34) Sig: SIG_TEXT (0x00000019) "APK:Flat:Plaintext/UTF8"
0011.blk : Scan 0x00000000 - 0x0000027d (0 - 637) Sig: SIGNUM_APK (0x00000062) "APK:APK block"
"""


if __name__ == "__main__":
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.WARNING)
    channel = logging.StreamHandler()
    channel.setLevel(logging.WARNING)
    logger.addHandler(channel)

    with os.scandir(path) as it:
        for entry in it:
            if entry.name.endswith('.log') and entry.is_file():
                basename=entry.name.rsplit('.', 1)
                if not basename or not basename[0]:
                    continue
                logger.info("processing block %s. basename = %s" % (entry.name, basename[0]))
                with open(entry.path) as f:
                    for line in f:
                        m = regexp.match(line)
                        (blk, blk_type) = (m.group(1), m.group(2))
                        logger.info("%s,%s" %(blk, blk_type))
                        if blk_type =="SIGNUM_DEX_OPCODE_NORMALIZED":
                            blkname=basename[0] + ".%s" % blk
                            # analyse and extract from the binary block "blkname"       # XXX FIXME: think about spawning this off as a parallel thread/task in dask?
                            print(blkname)
                        else:
                            logger.info("ignoring block file %s" % (basename[0] + ".%s" %blk))
                            continue
