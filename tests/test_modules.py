import unittest2 as unittest
from drogon.system.downloader.requests_downloader import RequestsDownloader
from drogon.system.scheduler.queue import PriorityRequestQueue
from drogon.system.engine.engine_core import EngineCore
from drogon.system.spider.base_spider import BaseSpider
from drogon.system.pipeline.base_pipeline import BasePipeline
from drogon.system.pipeline.save_resp_pipeline import SaveRespPipeline
from drogon.settings import *
from drogon.system.result import Result

# class TestDownloader(unittest.TestCase):
#     def test_request_downloader(self):
#         request = Request(
#             url='http://www.cnblogs.com/jhao/p/7243043.html',
#         )
#         batch = [request,]
#         downloader = RequestsDownloader()
#         resps = downloader.download(batch)
#         for resp in resps:
#             if not resp.response:
#                 print('download fail')
#             else:
#                 print(resp)
#
# class TestQueue(unittest.TestCase):
#     baidu = BaiduSpider()
#     req = baidu.deom_request()
#     queue = PriorityQueue(baidu)
#     queue.push(req)
#     print(len(queue))
#     req = queue.pop()
#     print(req.url)
#     req.callback()
#     req.errback()

class BaiduSpider(BaseSpider):
    spider_id = 'baidu_id'

    MAX_RETRY_TIMES = 2

    def __init__(self):
        super(BaiduSpider, self).__init__(self.spider_id)
        self.logger.info('INIT')
        self.start_requests = [self.fetch(url='http://www.baidu.com', meta={'use_proxy': True})]

    def on_start(self, data):
        return self.fetch(url=data, meta={'use_proxy': True})

    def parse(self, response):
        if not response.response or response.response.status_code!=200:
            yield self.retry_get(response)
        else:
            self.logger.info('[SUCCESS] {}'.format(response.request.url))
            yield response


    def parse_retry(self, response):
        print('retry....')

    def parse_page(self, response):
        print('goodbye')

class TestEngine(object):
    engine = EngineCore(spider=BaiduSpider())
    engine.start()

if __name__ == '__main__':
    unittest.main()