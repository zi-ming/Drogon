"""
    base_downloader.py
    ~~~~~~~
    the Base class of downloader
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-02
    :python version: 3.6
"""
import requests

from drogon.system.downloader.modules.response import Response
from drogon.settings import DEFAULT_HEADERS

class BaseDownloader(object):
    def downloader(self, request):
        raise NotImplementedError

    @staticmethod
    def get(url, headers=None, encoding=True):
        if not headers:
            headers = DEFAULT_HEADERS
        resp = requests.get(url, headers=headers, verify=False)
        if encoding:
            resp = Response.encode_response(resp)
        return resp