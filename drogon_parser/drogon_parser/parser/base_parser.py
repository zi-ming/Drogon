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
import time
import json
import threading
import asyncio
import types
import traceback

from queue import Queue
from queue import Empty

from drogon_parser.settings import SAMPLE_PATH, RESULT_PATH, CONCURRENT_SIZE
from drogon_parser.logger import Logger
from drogon_parser.utils import *

class BaseParser(object):
    parser_name = None


    def __init__(self):
        self.logger = Logger(self.parser_name).logger
        path = os.path.join(RESULT_PATH, self.parser_name)
        if not os.path.exists(path):
            os.mkdir(path)
        self.result_path = os.path.join(path, self.parser_name)
        if os.path.exists(self.result_path):
            os.remove(self.result_path)
        self.sample_path = os.path.join(SAMPLE_PATH, self.parser_name)
        if not os.path.exists(self.sample_path):
            raise IOError('sample path not exists: {}'.format(self.sample_path))
        self.file_path_queue = Queue(maxsize=2000)
        self.result_queue = Queue()
        self.status = 'started'

    def read_files(self):
        for _, _, files in os.walk(self.sample_path):
            for f in files:
                self.file_path_queue.put(os.path.join(self.sample_path, f))

    def write_result(self):
        retry_count = 0
        with open(self.result_path, 'a', encoding='utf-8') as f:
            while True:
                try:
                    content = self.result_queue.get(False)
                    f.write('{}\n'.format(content))
                    retry_count = 0
                except:
                    if self.file_path_queue.empty():
                        retry_count += 1
                        time.sleep(1)
                    if retry_count == 5:
                        self.status = 'stopped'
                        break

    def parse(self, content):
        pass

    def on_start(self):
        read_thread = threading.Thread(target=self.read_files)
        write_thread = threading.Thread(target=self.write_result)
        read_thread.start()
        write_thread.start()

        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(CONCURRENT_SIZE):
            tasks.append(asyncio.ensure_future(self.on_parser()))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        read_thread.join()
        write_thread.join()

    async def on_parser(self):
        while self.status == 'started':
            try:
                file_path = self.file_path_queue.get(False)
                content = open(file_path, encoding='utf-8').read()
                callback = self.parse(content)
                if isinstance(callback, types.GeneratorType):
                    for ret in callback:
                        if isinstance(ret, dict):
                            self.result_queue.put(json.dumps(ret, ensure_ascii=False))
                elif isinstance(callback, dict):
                    self.result_queue.put(json.dumps(callback, ensure_ascii=False))
            except Empty:
                time.sleep(0.1)
            except:
                print(traceback.format_exc())
                pass
