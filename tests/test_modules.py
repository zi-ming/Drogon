import unittest2 as unittest
from drogon.system.downloader.http.request import Request
from drogon.system.downloader.requests_downloader import RequestsDownloader
from drogon.system.scheduler.queue import PriorityQueue
from drogon.system.engine.engine_core import EngineCore

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

# class BaiduSpider(object):
#     spider_id = 'baidu_id'
#     spider_name = 'baidu_name'
#
#     def deom_request(self):
#         return Request(
#             url='http://www.baidu.com',
#             callback=self.demo_func,
#             errback=self.demo_func
#         )
#
#     def demo_func(self):
#         print('pass test')
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
    engine = EngineCore()
    engine.start()
    # def test_start(self):
    #     engine = EngineCore()
    #     engine.start()

if __name__ == '__main__':
    unittest.main()