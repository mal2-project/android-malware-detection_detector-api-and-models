"""
This file contains fixtures which can be used by any unit-test
from any file at the same level or below it
"""

import pytest
from _pytest.monkeypatch import MonkeyPatch
import datetime
import os
import time
import psycopg2
from typing import NamedTuple, Optional

# local imports
import server
from malware_cache import FileEntry, FileEntryCache
from config import config

# ==================================== constants ====================================

CONSTANTS = dict(
    MOCK_FILE_CREATION_DATETIME=datetime.datetime(1999, 12, 31, 1, 1, 1),
    MOCK_FILE_ANALYSIS_DATETIME=datetime.datetime(2001, 1, 1, 2, 2, 2),
    CACHE=FileEntryCache(),
    MOCK_APK_TESTFILE_PATH="./tests/mocks/brilliant.apk",
    MOCK_APK_TESTFILE_NAME="brilliant.apk",
    MOCK_NON_APK_TESTFILE_PATH="./tests/mocks/invalid_file.txt",
    MOCK_NON_APK_TESTFILE_NAME="invalid_file.txt",
    MOCK_TIME=42,
    MOCK_PID=21,
    UPLOAD_URL="/api/v1/upload/binary/",
    VALID_APK_SIGNATURE="application/vnd.android.package-archive",
    INVALID_APK_SIGNATURE="not/valid.signature",
    CONTAINS_TRACKERS_STUB=True,
    CONTAINS_MALWARE_STUB=False,
    CONTAINS_ADWARE_STUB=False)

#  FileEntry examples

EXAMPLE_1 = FileEntry(filename='foo',
                      path='imaginary',
                      md5='123',
                      sha1='234',
                      sha256='345',
                      contains_malware=True,
                      contains_adware=False,
                      contains_trackers=True)

EXAMPLE_2 = FileEntry(filename='bar',
                      path='this/file/should/never/be/uploaded/into/the/cache',
                      md5='13',
                      sha1='24',
                      sha256='35',
                      contains_malware=False,
                      contains_adware=True,
                      contains_trackers=False)

EXAMPLE_3 = FileEntry(filename='bar',
                      path='stairway/to/heaven',
                      md5='14',
                      sha1='25',
                      sha256='36',
                      contains_malware=False,
                      contains_adware=True,
                      contains_trackers=False)
# first_seen has to be set after creation since it is not a valid parameter for __init__
EXAMPLE_3.first_seen = CONSTANTS['MOCK_FILE_CREATION_DATETIME']

EXAMPLE_4 = FileEntry(filename='bar',
                      path='highway/to/hell',
                      md5='12',
                      sha1='23',
                      sha256='34',
                      contains_malware=False,
                      contains_adware=True,
                      contains_trackers=False)
# first_seen has to be set after creation since it is not a valid parameter for __init__
EXAMPLE_4.first_seen = CONSTANTS['MOCK_FILE_CREATION_DATETIME']
# analyzed_at has to be set after creation since it is not a valid parameter for __init__
EXAMPLE_4.analyzed_at=CONSTANTS['MOCK_FILE_ANALYSIS_DATETIME']

FILE_ENTRY_EXAMPLES = {'FILE_ENTRY_NOT_YET_IN_CACHE': EXAMPLE_1,
                       'FILE_ENTRY_NEVER_IN_CACHE': EXAMPLE_2,
                       'FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_BUT_NOT_YET_ANALYZED': EXAMPLE_3,
                       'FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_AND_ALREADY_ANALYZED': EXAMPLE_4}

# ==================================== Exceptions ====================================


class FailedSetupException(Exception):
    """should be raised if there is a problem during fixture SETUP"""


# ==================================== fixtures ====================================


@pytest.fixture(scope='module', autouse=True)
def setup_mock_constants():
    """
    replace os.getpid() and time.time() as well as datetime.datetime.now()
    which are called in server.py by a constant value lambda function
    to ensure consistency during testing
    :return: None
    """
    mp = MonkeyPatch()
    mp.setattr(time, 'time', lambda: CONSTANTS['MOCK_TIME'])
    mp.setattr(os, 'getpid', lambda: CONSTANTS['MOCK_PID'])

    # it's a bit less straightforward to monkeypatch datetime.datetime.now
    # see: https://stackoverflow.com/questions/20503373/how-to-monkeypatch-pythons-datetime-datetime-now-with-py-test
    class MockDatetime:

        def __init__(self, *args, **kwargs):
            # TODO: temporary fix for unittests
            pass

        @classmethod
        def now(cls):
            return CONSTANTS['MOCK_FILE_CREATION_DATETIME']

    mp.setattr(datetime, 'datetime', MockDatetime)


def reset_table(self) -> None:
    """Delete every row (entry) in the mock table, should be called during setup/teardown"""
    with self.db_conn.cursor() as curs:
        query = "DELETE FROM cache;"
        curs.execute(query)


def is_empty(self) -> bool:
    """Return True if table is empty (no rows), else False"""
    with self.db_conn.cursor() as curs:
        query = "SELECT COUNT (*) FROM cache;"
        curs.execute(query)
        result = curs.fetchone()
        return result[0] == 0


@pytest.fixture(scope='module', autouse=True)
def add_test_methods_to_FileEntryCache() -> None:
    """
    adds the methods "reset_table" and "is_empty" to the FileEntry class for the unit-tests
    reset_table will delete every row in the table to ensure empty tables for the tests
    is_empty will return True if the table is empty, else False
    :return: None
    """
    monkeypatch = MonkeyPatch()
    monkeypatch.setattr(FileEntryCache, 'reset_table', reset_table)
    monkeypatch.setattr(FileEntryCache, 'is_empty', is_empty)


@pytest.fixture
def setup_empty_db() -> None:
    """
    produce an empty table in the database for unit-tests
    :return: None
    """
    # create testdatabase and empty it before first use
    global CONSTANTS

    cache = CONSTANTS['CACHE']
    cache.reset_table()
    assert cache.is_empty()  # sanity check: table should be empty now

    # replace database used by server with our testdatabase
    # https://github.com/pytest-dev/pytest/issues/363
    monkeypatch = MonkeyPatch()
    monkeypatch.setattr(server, 'cache', CONSTANTS['CACHE'])


@pytest.fixture
def setup_non_empty_db(setup_empty_db) -> None:
    """
    produce a database with a select few examples for unit-tests

    contains the following files:
    - CONSTANTS['FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_AND_ALREADY_ANALYZED']
    - CONSTANTS['FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_BUT_NOT_YET_ANALYZED']

    :return: None
    """

    # inserts an entry into the BinCache

    try:
        db_conn = psycopg2.connect(dbname=config['DATABASE'],
                                   user=config['USERNAME'],
                                   password=config['PASSWORD'],
                                   host=config['DBHOST'])
        db_conn.set_session(autocommit=True)

        sql_query = '''INSERT INTO "cache" (
                            filename, 
                            path_on_disk, 
                            md5, 
                            sha1, 
                            sha256, 
                            contains_malware, 
                            contains_trackers, 
                            contains_adware, 
                            first_seen, 
                            analyzed_at
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), %s)'''
        cur = db_conn.cursor()
        for example in (FILE_ENTRY_EXAMPLES['FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_AND_ALREADY_ANALYZED'],
                        FILE_ENTRY_EXAMPLES['FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_BUT_NOT_YET_ANALYZED']):
            cur.execute(sql_query, (
                example.filename,
                example.path,
                example.md5,
                example.sha1,
                example.sha256,
                example.contains_malware,
                example.contains_trackers,
                example.contains_adware,
                example.analyzed_at))
            assert cur.rowcount == 1  # otherwise nothing was updated
    except Exception as err:
        raise FailedSetupException(str(err))
