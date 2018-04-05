import unittest2 as unittest
from drogon.system.downloader.http.request import Request
from drogon.system.downloader.requests_downloader import RequestsDownloader

class TestDownloader(unittest.TestCase):
    def test_request_downloader(self):
        request = Request(
            url='http://www.cnblogs.com/jhao/p/7243043.html',
        )
        batch = [request,]
        downloader = RequestsDownloader()
        resps = downloader.download(batch)
        for resp in resps:
            if not resp.response:
                print('download fail')
            else:
                print(resp)

if __name__ == '__main__':
    unittest.main()