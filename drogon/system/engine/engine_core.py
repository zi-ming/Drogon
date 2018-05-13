"""
    engine_core.py
    ~~~~~~~
    Responsible for the scheduling of each module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import re
import time
import uuid
import traceback
import types

from drogon.settings import IDLE_TIME
from drogon.settings import SPIDER_STOP_TIME
from drogon.settings import REQUEST_BATCH_SIZE
from drogon.settings import LEGAL_STATUS_CODE

from drogon.system.downloader.requests_downloader import RequestsDownloader as Downloader
from drogon.system.downloader.modules.request import Request
from drogon.system.downloader.proxy import handle_request_proxy

from drogon.system.logger import sys_logger as logger

from drogon.system.scheduler.queue import PriorityRequestQueue as Scheduler
from drogon.system.scheduler.queue import SpiderStats
from drogon.system.scheduler.queue import CrawlStatus
from drogon.system.scheduler.queue import ProxyQueue

from drogon.system.pipeline.base_pipeline import BasePipeline
from drogon.system.pipeline.save_result_pipeline import SaveResultPipeline as Pipeline

class EngineCore(object):
    def __init__(self, spider=None, downloader=None, pipeline=None,
                 scheduler=None, batch_size=1):
        self._spider = spider
        self._spider_id = spider and spider.spider_id or None
        self._batch_size = batch_size - 1 or REQUEST_BATCH_SIZE
        self._pipelines = dict()
        if not pipeline:
            self.set_pipeline(Pipeline())
        elif isinstance(pipeline, dict):
            self._pipelines = pipeline
        elif isinstance(pipeline, BasePipeline):
            self.set_pipeline(pipeline)
        if not downloader:
            self._downloader = Downloader()
        else:
            self._downloader = downloader()
        if not scheduler:
            self._scheduler = Scheduler
        else:
            self._scheduler = scheduler
        SpiderStats.set_stop_stats(self._spider_id)

    def set_spider(self, spider):
        self._spider = spider
        self._spider_id = spider.spider_id
        return self

    def set_scheduler(self, scheduler):
        self._scheduler = scheduler
        return self

    def set_downloader(self, downloader):
        self._downloader = downloader()
        return self

    def set_pipeline(self, pipeline, name=None):
        if not name:
            name = str(uuid.uuid1())
        self._pipelines[name] = pipeline
        return self

    def start(self):
        try:
            self.clean()
            logger.info("[{}] STARTED".format(self._spider_id))
            SpiderStats.set_started_stats(self._spider_id)
            self._request_queue = self._scheduler(self._spider)
            for request in self._spider.start_requests or \
                    self._spider.on_message() or []:
                if not request or not isinstance(request, Request):
                    continue
                self._request_queue.push(request)
                logger.debug('[{}] start request: {}'.format(self._spider_id, request))
                if not SpiderStats.is_started_stats(self._spider_id):
                    break
            for batch in self._batch_requests():
                if batch:
                    self._crawl(batch)
                else:
                    time.sleep(3)
                    logger.info('[{}] crawl page count: {}'.format(
                        self._spider_id, CrawlStatus.get_status(self._spider_id)))
            SpiderStats.set_stop_stats(self._spider_id)
            logger.info('[{}] FINISH'.format(self._spider_id))
        except:
            logger.error('[{}] EXCEPTION: {}'.format(self._spider_id, traceback.format_exc()))
        finally:
            pass
            # self.clean()

    def _batch_requests(self):
        batch, count = [], 0
        while True:
            if not SpiderStats.is_started_stats(self._spider_id):
                time.sleep(2)
                yield []
                continue
            count += 1
            if count > REQUEST_BATCH_SIZE:
                batch.sort(key=lambda x:x.priority, reverse=True)
                yield batch
                batch = []
                count = 0
            request = self._request_queue.pop()
            if request:
                if not request.callback:
                    request.callback = self._spider.parse
                if not request.errback:
                    request.errback = request.callback
                batch.append(request)

    def _crawl(self, batch):
        responses = self._downloader.download(batch)
        for response in responses:
            if not response.response or response.response.status_code not in LEGAL_STATUS_CODE:
                callback = response.request.errback(response)
            else:
                callback = response.request.callback(response)
            if isinstance(callback, types.GeneratorType):
                scheduler_pipe = self._request_queue.get_pipeline()
                for item in callback:
                    if isinstance(item, Request):
                        self._request_queue.push_pipe(item, scheduler_pipe)
                        logger.debug('[{}] start request: {}'.format(self._spider_id, item))
                    else:
                        for pipeline in self._pipelines.values():
                            pipeline.parse(item, self._spider)
                scheduler_pipe.execute()
            elif isinstance(callback, Request):
                self._request_queue.push(callback)
                logger.debug('[{}] start request: {}'.format(self._spider_id, callback))
            else:
                for pipeline in self._pipelines.values():
                    pipeline.parse(callback, self._spider)

    def clean(self):
        CrawlStatus.clean(self._spider_id)
        SpiderStats.clean(self._spider_id)
        ProxyQueue.clean()