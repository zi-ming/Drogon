import unittest2 as unittest
from drogon.system.downloader.http.request import Request
from drogon.system.downloader.requests_downloader import RequestsDownloader
from drogon.system.scheduler.queue import PriorityQueue
from drogon.system.engine.engine_core import EngineCore
from drogon.system.spider.base_spider import BaseSpider

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


class TestEngine(object):
    class BaiduSpider(BaseSpider):
        spider_id = 'baidu_id'
        spider_name = 'baidu_name'
        start_requests = [Request(url='http://www.jb51.net')]

        def parse(self, response):
            yield Request(
                url='http://www.sogou.com',
                callback=self.parse_page,
                errback=self.parse_retry
            )

        def parse_retry(self, response):
            print('retry....')

        def parse_page(self, response):
            print('goodbye')

    engine = EngineCore(spider=BaiduSpider())
    engine.start()

if __name__ == '__main__':
    unittest.main()