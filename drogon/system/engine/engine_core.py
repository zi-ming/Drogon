import re
import time
import uuid
import traceback
import types

from drogon.settings.default_settings import IDLE_TIME, SPIDER_STOP_TIME
from drogon.settings.default_settings import REQUEST_BATCH_SIZE
from drogon.system.downloader.requests_downloader import RequestsDownloader
from drogon.system.scheduler.queue import PriorityQueue
from drogon.system.utils import logger
from drogon.system.utils.engine import read_start_urls_from_file
from drogon.system.downloader.http.request import Request
from drogon.settings.default_settings import LEGAL_STATUS_CODE


class EngineCore(object):
    def __init__(self, spider=None, downloader=None, pipeline_dict=None,
                 scheduler=None, batch_size=1, time_sleep=None):
        self._spider = spider
        self._spider_name = spider and spider.spider_name or None
        self._spider_id = spider and spider.spider_id or None
        self._host_regex = spider and self._get_host_regex() or None
        self._spider_status = 'stopped'
        self._pipelines = pipeline_dict or dict()
        self._batch_size = batch_size - 1 or REQUEST_BATCH_SIZE
        self._downloader = downloader or RequestsDownloader
        if not downloader:
            self._downloader = RequestsDownloader()
        else:
            self._downloader = downloader()

    def set_spider(self, spider):
        self._spider = spider
        self._spider_name = spider.spider_name
        self._spider_id = spider.spider_id
        self._host_regex = self._get_host_regex()
        return self

    def set_scheduler(self, scheduler):
        self._request_queue = scheduler
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
            logger.info("START '%s' SUCCESS"%(self._spider_id))
            self._spider_status = 'started'
            self._request_queue = PriorityQueue(self._spider)
            for request in self._spider.start_requests or \
                    self.handle_file_start_urls() or []:
                self._request_queue.push(request)
                logger.info('start request: %s'%(request))

            idle_count = 0
            for batch in self._batch_requests():
                if batch:
                    self._crawl(batch)
                    logger.info('handle response')
                    idle_count = 0
                else:
                    idle_count += 1
                    if idle_count > (SPIDER_STOP_TIME*300):
                        logger.info('SPIDER FINISH')
                        break
                    elif idle_count % (IDLE_TIME*300) == 0:
                        logger.debug('waiting for request...')
                    time.sleep(0.001)
            self._spider_status = 'stopped'
            logger.info('STOP %s SUCCESS'%(self._spider_id))
        except:
            logger.error('EXCEPTION[%s]: %s'%(self._spider_id, traceback.format_exc()))

    def _batch_requests(self):
        batch = []
        count = 0
        while True:
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

    def handle_file_start_urls(self):
        for url in read_start_urls_from_file(self._spider):
            req = Request(url=url, **self._spider.spider_settings)
            yield req

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
                        logger.info('start request: %s' % (item))
                    else:
                        for pipeline in self._pipelines.values():
                            pipeline.parse(item, self._spider)
                scheduler_pipe.execute()
            elif isinstance(callback, Request):
                self._request_queue.push(callback)
                logger.info('start request: %s' % (callback))
            else:
                for pipeline in self._pipelines.values():
                    pipeline.parse(callback, self._spider)

    def _get_host_regex(self):
        allowed_domains = getattr(self._spider, 'allowed_domains', None)
        if not allowed_domains:
            return re.compile('')
        regex = r'^(.*\.)?(%s)(\..*)?$'%(
            '|'.join([re.escape(x) for x in allowed_domains]))
        return re.compile(regex)