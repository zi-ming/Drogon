"""
    base_parser.py
    ~~~~~~~
    a base class of parser
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-16
    :python version: 3.6
"""

import os
import json
import types

from drogon_parser.settings import SAMPLE_PATH, RESULT_PATH
from drogon_parser.logger import Logger
from drogon_parser.utils import *

class BaseParser(object):
    parser_name = None

    def __init__(self):
        self.logger = Logger(self.parser_name).logger

    def parse(self, content):
        pass

    def on_start(self):
        path = os.path.join(SAMPLE_PATH, self.parser_name)
        if not os.path.exists(path):
            raise 'sample path not exists: {}'.format(path)
        for _, _, files in os.walk(path):
            files = sorted(files)
            for f in files:
                content = open(os.path.join(path, f), encoding='utf-8').read()
                callback = self.parse(content)
                if isinstance(callback, types.GeneratorType):
                    for ret in callback:
                        if isinstance(ret, dict):
                            self.local_save(ret)
                elif isinstance(callback, dict):
                    self.local_save(callback)

    def local_save(self, data):
        if not isinstance(data, dict):
            raise TypeError
        path = os.path.join(RESULT_PATH, self.parser_name)
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, get_timestamp())
        data = json.dumps(data, ensure_ascii=False)
        with open(path, 'a') as f:
            f.write('{}\n'.format(data))

