import re
from drogon.settings.default_settings import ENGINE_SCHEDULER_SLEEP
from drogon.settings.default_settings import REQUEST_BATCH_SIZE
from drogon.system.downloader.requests_downloader import RequestsDownloader
from drogon.system.scheduler


class EngineCore(object):
    def __init__(self, spider, downloader=None, pipelines=None,
                 scheduler=None, batch_size=None, time_sleep=None):
        self._spider = spider
        self._host_regex = self._get_host_regex()
        self._spider_status = 'stopped'
        self._pipelines = pipelines or dict()
        self._time_sleep = time_sleep or ENGINE_SCHEDULER_SLEEP
        self._batch_size = batch_size or REQUEST_BATCH_SIZE
        self._spider_name = spider.spider_name
        self._spider_id = spider.spider_id
        self._downloader = downloader or RequestsDownloader
        self._request_queue =




    def _get_host_regex(self):
        allowed_domains = getattr(self._spider, 'allowed_domains', None)
        if not allowed_domains:
            return re.compile('')
        regex = r'^(.*\.)?(%s)(\..*)?$'%(
            '|'.join([re.escape(x) for x in allowed_domains]))
        return re.compile(regex)