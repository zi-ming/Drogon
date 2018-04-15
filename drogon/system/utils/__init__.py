"""
    utils
    ~~~~~~~
    commonly used tools
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import os
import six

from drogon.settings import START_URLS_PATH

def to_unicode(text, encoding=None, errors='strict'):
    if not isinstance(text, bytes):
        return text
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)

def read_line_from_start_url_files(spider_id):
    path = os.path.join(START_URLS_PATH, spider_id)
    if not os.path.exists(path):
        return None
    for _, _, files in os.walk(path):
        files = sorted(files)
        for f in files:
            with open(os.path.join(path, f)) as f:
                for line in f:
                    yield line