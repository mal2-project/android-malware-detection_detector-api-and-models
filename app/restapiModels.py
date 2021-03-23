#!/usr/bin/env python

from typing import List, Dict
from pydantic import BaseModel

""" Example response (JSON)

{
  "uploaded_file": "/tmp/BAWAG.apk",
  "already_analyzed": false,
  "md5": "1c581611eb8e2ab5d947ed481e96f59b",
  "sha1": "d69e12ba01c9373ae4da083df65466d5cafb7a25",
  "sha256": "239e856979cf26ac999a83bd94d1984a38d65a7dcc6022c83ede2f97b937d60f",
  "query_time_sec": 0.7,
  "classification": {
    "MALWARE": 0.9,
    "BENIGN": 0.1
  },
  "extra": {}
}
"""


class ResponseModel(BaseModel):
    uploaded_file: str
    stored_path: str
    already_analyzed: bool
    query_time_sec: float
    md5: str
    sha1: str
    sha256: str
    classification: Dict[str, float]
    extra: Dict = None
