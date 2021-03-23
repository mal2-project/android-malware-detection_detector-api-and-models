
"""
Config file
"""

import sys
import os
import logging

config = dict()
config.update(dict(
    version=0.5,
    debug=True,
    DATABASE=os.getenv('DB_NAME'),
    USERNAME=os.getenv('DB_USER'),
    PASSWORD=os.getenv('DB_PASSWORD'),
    DBHOST='localhost',
    DBPORT=5432,
    SECRET_KEY="Please generate a really long random string here",
    UPLOAD_PATH="/tmp",            # Change to the upload path where files should be stored. Make sure this has enough disk space.
))


LOG_FORMAT_SYSLOG = '%(name)s: %(levelname)s %(message)s'
logger = logging.getLogger(sys.argv[0])
