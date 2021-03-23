"""Testing the server module
Requires:
pytest (version == 5.3.1)
pytest-asyncio (version == 0.10.0)
pytest-trio (version == 0.5.2)
pytest_tornasync (version == 0.6.0.post2)


To run tests just enter the apk-total directory in terminal and run the command:
pytest -v

To run all tests in a file just add the filename:
pytest -v test_server.py

To run just a single test in a file, add "::testname" (without quotation marks), for example:
pytest -v test_server.py::test_upload_no_file_response_status
"""
import pytest
import main
import os
import time
from main import app
from typing import BinaryIO
from starlette.testclient import TestClient
from unittest.mock import patch, MagicMock as Mock

from conftest import CONSTANTS as CONS, FILE_ENTRY_EXAMPLES as EX

client = TestClient(app)


# ============================================= testing main server =============================================


def test_upload_no_file_response_status(setup_empty_db):
    """Test response status when no file is uploaded"""
    # GIVEN an empty database

    # WHEN calling the post method for uploading files without adding a file
    response = client.post(CONS['UPLOAD_URL'])

    # THEN we expect a Validation Error (status code=422)
    assert response.status_code == 422


def test_upload_no_file_response_json(setup_empty_db):
    """Test json response when no file is uploaded"""
    # GIVEN an empty database

    # WHEN calling the post method for uploading files without adding a file
    response = client.post(CONS['UPLOAD_URL'])

    # THEN we expect the response JSON to tell us that a file is missing
    assert response.json() == {'detail': [{'loc': ['body', 'file'],
                                           'msg': 'field required',
                                           'type': 'value_error.missing'}]}


def test_upload_invalid_file_response_status(setup_empty_db):
    """Test response status when a file that is not a valid .apk file (by content_type) is uploaded"""
    test_file: BinaryIO

    # GIVEN an empty database and an invalid file (not apk)

    # WHEN we upload that invalid file
    with open(CONS['MOCK_NON_APK_TESTFILE_PATH'], mode='rb') as test_file:
        # files argument format: {'file': (<filename>, <filecontent>, <content_type>)}
        # see: https://2.python-requests.org/en/master/user/quickstart/#post-a-multipart-encoded-file
        files = {'file': (CONS['MOCK_NON_APK_TESTFILE_NAME'], test_file, CONS['INVALID_APK_SIGNATURE'])}
        response = client.post(CONS['UPLOAD_URL'], files=files)

    # THEN we expect a Bar Request (Error: 400) returned
    assert response.status_code == 400


def test_upload_invalid_file_response_json(setup_empty_db):
    """Test json response when a file that is not a valid .apk file (by content_type) is uploaded"""
    test_file: BinaryIO

    # GIVEN an empty database and an invalid file (not apk)

    # WHEN we upload that invalid file
    with open(CONS['MOCK_NON_APK_TESTFILE_PATH'], mode='rb') as test_file:
        # files argument format: {'file': (<filename>, <filecontent>, <content_type>)}
        # see: https://2.python-requests.org/en/master/user/quickstart/#post-a-multipart-encoded-file
        files = {'file': (CONS['MOCK_NON_APK_TESTFILE_NAME'], test_file, CONS['INVALID_APK_SIGNATURE'])}
        response = client.post(CONS['UPLOAD_URL'], files=files)

    # THEN we expect the response JSON to tell us that it only accepts Android APK files
    assert response.json() == {"detail": "I only accept Android APK files as input."}


def test_upload_already_cached_valid_apk_file_response_status(setup_empty_db):
    test_file: BinaryIO
    # GIVEN a empty database
    #       and a valid apk file

    # WHEN we upload a valid file to the database twice
    with open(CONS['MOCK_APK_TESTFILE_PATH'], mode='rb') as test_file:
        # note we manually have to set the content_type to the correct value for this test to work
        # files argument format: {'file': (<filename>, <filecontent>, <content_type>)}
        # see: https://2.python-requests.org/en/master/user/quickstart/#post-a-multipart-encoded-file
        files = {'file': (CONS['MOCK_APK_TESTFILE_NAME'], test_file, CONS['VALID_APK_SIGNATURE'])}

        # upload the file once to ensure it is in cache
        response = client.post(CONS['UPLOAD_URL'], files=files)

        # sanity check: ensure that first upload also got correct response status
        assert response.status_code == 200

        # upload again to test the response to an already cached file
        response2 = client.post(CONS['UPLOAD_URL'], files=files)

    # THEN it will return a succesful response (status code = 200)
    assert response2.status_code == 200


def test_upload_already_cached_valid_apk_file_json_response(setup_empty_db):
    test_file: BinaryIO
    # GIVEN an empty database
    #       and a valid apk file

    # WHEN we upload a file twice
    for _ in range(2):
        with open(CONS['MOCK_APK_TESTFILE_PATH'], mode='rb') as test_file:

            # note we manually have to set the content_type to the correct value for this test to work
            # files argument format: {'file': (<filename>, <filecontent>, <content_type>)}
            # see: https://2.python-requests.org/en/master/user/quickstart/#post-a-multipart-encoded-file
            files = {'file': (CONS['MOCK_APK_TESTFILE_NAME'], test_file, CONS['VALID_APK_SIGNATURE'])}

            response = client.post(CONS['UPLOAD_URL'], files=files)

    # THEN the response json on the second status should look as follows:
    assert response.json() == {"uploaded_file": f"{CONS['MOCK_APK_TESTFILE_NAME']}",
                               "stored_path": f"/tmp/{CONS['MOCK_APK_TESTFILE_NAME']}.387ea496db2bf09f42bde63e4751fdbbf977d82ae26e21fcdbc3d691a5c47f11.21.apk",
                               f"already_analyzed": True,
                               "md5": "cc9fd9707cd830609375edfd4341ba85",  # TODO: monkeypatch hashing for single tests
                               "sha1": "4a1a5ac1050ad08397d208eeb7ca715447f4f9dd",
                               "sha256": "387ea496db2bf09f42bde63e4751fdbbf977d82ae26e21fcdbc3d691a5c47f11",
                               "classification": {
                                   "contains_malware": CONS['CONTAINS_MALWARE_STUB'],
                                   "contains_trackers": CONS['CONTAINS_TRACKERS_STUB'],
                                   "contains_adware": CONS['CONTAINS_ADWARE_STUB']
                               },
                               "extra": {'meta': {'query-duration [sec]': 0}}}


def test_sha256_not_in_cache():
    cached = main.is_cached("this string should NOT be in the cache/database")
    assert cached is False


@pytest.mark.xfail(reason='''
main.is_cached expects sha256 but then calls the malware_cache.FileEntryCache
__contains__ method (with that sha256) but __contains__ only takes FileEntry as arg, not sha256''')
def test_sha256_in_cache(setup_non_empty_db):
    # GIVEN a database with some files already stored

    # WHEN we ask if the sha256 of one of the cached files is in the cache
    cached = main.is_cached(sha256=EX['FILE_ENTRY_IN_DB_WITH_FIRST_SEEN_BUT_NOT_YET_ANALYZED'].sha256)

    # THEN that should be True
    assert cached is True


@pytest.mark.skip(reason='not properly implemented yet')
@pytest.mark.asyncio()
async def test_file_validation_success():
    # TODO: this test is not good enough (only tests if the function initial_check_file()
    # TODO:     calls file.content_type => find a way for it to handle an actual file
    mock_file = Mock()
    mock_file.content_type = CONS['VALID_APK_SIGNATURE']
    is_valid = await main.initial_check_file(mock_file)
    assert is_valid is True


@pytest.mark.skip(reason='not properly implemented yet')
@pytest.mark.asyncio()
async def test_file_validation_failure():
    # TODO: this test is not good enough (only tests if the function initial_check_file()
    # TODO:     calls file.content_type => find a way for it to handle an actual file
    mock_file = Mock()  # TODO: set up mock database and replace with call to actual file
    mock_file.content_type = "not a valid apk file"
    with pytest.raises(main.HTTPException):
        is_valid = await main.initial_check_file(mock_file)
