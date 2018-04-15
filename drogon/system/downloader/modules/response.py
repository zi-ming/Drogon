"""
    response.py
    ~~~~~~~
    Response module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import requests
from requests.models import Response as Response_obj

class Response(object):
    def __init__(self, response, request):
        self.response = response
        self.request = request

    @staticmethod
    def encode_response(response):
        encoding = response.encoding
        if encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(response.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = response.apparent_encoding
            response.encoding = encoding
        return response

    def __str__(self):
        if not self.response:
            return "<Response failed: %s>"%(self.request.url)
        if isinstance(self.response, Response_obj):
            return "<Response [%s] [%s] [%.2f KB]>"%(
                self.response.status_code, self.response.url, len(self.response.content) / 1000.0)
        else:
            return "<Response unknown:[%s] %s>"%(
                self.response.status_code, self.response.url)
    __repr__ = __str__