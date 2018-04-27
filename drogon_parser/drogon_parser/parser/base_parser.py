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

from multiprocessing import Process, Manager, Value, Array
from ctypes import c_char_p

from drogon_parser.settings import SAMPLE_PATH
from drogon_parser.settings import RESULT_PATH
from drogon_parser.settings import CONCURRENT_SIZE
from drogon_parser.settings import PROCESS_COUNT
from drogon_parser.settings import ASYN_COUNT
from drogon_parser.settings import MAX_IDLE_TIMES

from drogon_parser.logger import Logger
from drogon_parser.utils import *

class ParserStatus(object):
    stop_status = 0
    start_status = 1

class BaseParser(object):
    parser_name = ''

    def __init__(self):
        path = os.path.join(RESULT_PATH, self.parser_name)
        if not os.path.exists(path):
            os.mkdir(path)
        self.result_path = os.path.join(path, self.parser_name)
        if os.path.exists(self.result_path):
            os.remove(self.result_path)
        self.sample_path = os.path.join(SAMPLE_PATH, self.parser_name)
        if not os.path.exists(self.sample_path):
            raise IOError('sample path not exists: {}'.format(self.sample_path))

    def read_files(self, sample_path_queue):
        for _, _, files in os.walk(self.sample_path):
            for f in files:
                sample_path_queue.put(os.path.join(self.sample_path, f))

    def on_start(self):
        print('parser started')
        manager = Manager()
        process_list = []
        sample_path_queue = manager.Queue()
        result_queue = manager.Queue()
        status = Array('i', [ParserStatus.start_status,])
        process_list.append(Process(target=self.read_files, args=(sample_path_queue,)))
        process_list.append(Process(target=self.write_result, args=(status, sample_path_queue, result_queue)))
        for i in range(PROCESS_COUNT):
            process_list.append(Process(target=self.parser_factory, args=(status, sample_path_queue, result_queue)))

        for p in process_list:
            p.start()
        for p in process_list:
            p.join()

        print('Parser finished.')

    def write_result(self, status, sample_path_queue, result_queue):
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
                        status[0] = ParserStatus.stop_status
                        break
                except:
                    print(traceback.format_exc())

    def parser_factory(self, status, sample_path_queue, result_queue):
        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(ASYN_COUNT):
            tasks.append(asyncio.ensure_future(self.on_parser(status, sample_path_queue, result_queue)))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def on_parser(self, status, sample_path_queue, result_queue):
        while status[0]== ParserStatus.start_status:
            try:
                file_path = sample_path_queue.get(False)
                content = open(file_path, encoding='utf-8').read()
                callback = self.parse(content)
                if isinstance(callback, types.GeneratorType):
                    for ret in callback:
                        if isinstance(ret, dict):
                            result_queue.put(json.dumps(ret, ensure_ascii=False))
                elif isinstance(callback, dict):
                    print(callback)
                    result_queue.put(json.dumps(callback, ensure_ascii=False))
            except Empty:
                time.sleep(1)
            except:
                print(traceback.format_exc())

    def parse(self, content):
        pass
