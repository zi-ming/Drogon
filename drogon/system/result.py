
import os
import requests
from hashlib import md5
from drogon.settings.default_settings import RESULT_PATH

class Result(object):
    def __init__(self, response, spider, encoding=True):
        self.encoding = 'utf-8'
        if encoding:
            self.response = self.encode_response(response.response)
        else:
            self.response = response.response
        self.text = self.response.text
        self.content = self.response.content
        self.url = response.request.url
        self.request = response.request
        self.spider = spider
        self.result_id = md5(self.content).hexdigest()
        path = os.path.join(RESULT_PATH, self.spider.spider_id)
        self.path = os.path.join(path, self.result_id)


    def encode_response(self, response):
        encoding = response.encoding
        if encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(response.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = response.apparent_encoding
            self.encoding = encoding
            response.encoding = encoding
        return response


    def decode(self, encoding='utf-8'):
        self.content.decode(encoding)
        return self
