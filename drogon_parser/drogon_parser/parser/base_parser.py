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

from multiprocessing import Pool, Manager

from drogon_parser.settings import SAMPLE_PATH
from drogon_parser.settings import RESULT_PATH
from drogon_parser.settings import CONCURRENT_SIZE
from drogon_parser.settings import PROCESS_COUNT
from drogon_parser.settings import ASYN_COUNT
from drogon_parser.settings import MAX_IDLE_TIMES

from drogon_parser.logger import Logger
from drogon_parser.utils import *

class BaseParser(object):
    parser_name = ''

    def __init__(self):
        # self.logger = Logger(self.parser_name).logger
        path = os.path.join(RESULT_PATH, self.parser_name)
        if not os.path.exists(path):
            os.mkdir(path)
        self.result_path = os.path.join(path, self.parser_name)
        if os.path.exists(self.result_path):
            os.remove(self.result_path)
        self.sample_path = os.path.join(SAMPLE_PATH, self.parser_name)
        if not os.path.exists(self.sample_path):
            raise IOError('sample path not exists: {}'.format(self.sample_path))
        self.status = 'started'

    # @property
    # def parse_name(self):
    #     return self._parse_name
    #
    # @parse_name.setter
    # def parse_name(self, value):
    #     print('ok....')
    #     self._parse_name = value


    def read_files(self, sample_path_queue):
        print('ok')
        for _, _, files in os.walk(self.sample_path):
            for f in files:
                sample_path_queue.put(os.path.join(self.sample_path, f))

    def func(self):
        print('ok')

    def on_start2(self):
        manager = Manager()
        pool = Pool(processes=4)
        sample_path_queue = manager.Queue()
        pool.apply_async(func=self.func)
        pool.close()
        pool.join()

    def on_start(self):
        # self.logger = Logger(self.parser_name).logger
        print('parser started')
        manager = Manager()
        pool = Pool(processes=PROCESS_COUNT + 2)
        sample_path_queue = manager.Queue()
        result_queue = manager.Queue()
        pool.apply_async(func=self.func)
        # for i in range(PROCESS_COUNT):
        #     pool.apply_async(func=self.parser_factory, args=(sample_path_queue, result_queue))
        # pool.apply_async(func=self.write_result, args=(sample_path_queue, result_queue))
        pool.close()

        # while True:
        #     print(sample_path_queue.qsize())
        #     time.sleep(2)

        pool.join()
        print('Parser finished.')

    def write_result(self, sample_path_queue, result_queue):
        retry_count = 0
        with open(self.result_path, 'a', encoding='utf-8') as f:
            while True:
                try:
                    content = result_queue.get(False)
                    f.write('{}\n'.format(content))
                    retry_count = 0
                except Empty:
                    time.sleep(1)
                    if sample_path_queue.empty() and result_queue.empty():
                        retry_count += 1
                    if retry_count == MAX_IDLE_TIMES:
                        self.status = 'stopped'
                        break
                except:
                    self.logger.error('[EXCEPTION] {}'.format(traceback.format_exc()))

    def parser_factory(self, sample_path_queue, result_queue):
        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(ASYN_COUNT):
            tasks.append(asyncio.ensure_future(self.on_parser(sample_path_queue, result_queue)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def on_parser(self, sample_path_queue, result_queue):
        while self.status == 'started':
            try:
                file_path = sample_path_queue.get(False)
                content = open(file_path, encoding='utf-8').read()
                callback = self.parse(content)
                if isinstance(callback, types.GeneratorType):
                    for ret in callback:
                        if isinstance(ret, dict):
                            result_queue.put(json.dumps(ret, ensure_ascii=False))
                elif isinstance(callback, dict):
                    result_queue.put(json.dumps(callback, ensure_ascii=False))
            except Empty:
                time.sleep(0.1)
            except:
                self.logger.error('[EXCEPTION] {}'.format(traceback.format_exc()))

    def parse(self, content):
        pass


class BaseParser2(object):
    def func(self, x=None):
        print('ok')

    def on_start(self):
        manager = Manager()
        pool = Pool(processes=4)
        sample_path_queue = manager.Queue()
        pool.apply_async(func=self.func)
        pool.close()
        pool.join()

class Boss(BaseParser):
    parser_name = 'boss'