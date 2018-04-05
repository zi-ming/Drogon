"""
    base_downloader.py
    ~~~~~~~
    downloader of normal request
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-02
    :python version: 3.6
"""

import requests
import grequests
from requests.adapters import HTTPAdapter
from drogon.system.downloader.base_downloader import BaseDownloader
from drogon.system.downloader.proxy.proxy_pool import ProxyPool
from drogon.system.downloader.http.response import Response
from drogon.settings.default_settings import DEFAULT_HEADERS
from drogon.settings.default_settings import MAX_REQUEST_RETRY


class RequestsDownloader(BaseDownloader):
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self._retry_adapter = HTTPAdapter(max_retries=3)

    def download(self, batch):
        batch_requests = []
        for request in batch:
            session = requests.session()
            session.mount('http://', self._retry_adapter)
            session.mount('https://', self._retry_adapter)

            if not request.headers:
                request.headers = DEFAULT_HEADERS
            args = dict(
                session=session,
                url=request.url,
                headers=request.headers,
                cookies=request.cookies,
                verify=False,
                allow_redirects=request.allow_redirects,
                timeout=request.timeout
            )
            if request.use_proxy and len(self.proxy_pool):
                args['proxies'] = self.proxy_pool.get()
            if request.method.upper() == 'GET':
                batch_requests.append(grequests.get(**args))
            elif request.method.upper() == 'POST':
                args['data'] = request.data
                batch_requests.append(grequests.post(**args))
            else:
                pass

        ret_responses = []
        rets = grequests.map(batch_requests, exception_handler=exception_handler)
        for index, ret in enumerate(rets):
            ret_responses.append(Response(
                response=ret,
                request=batch[index]
            ))
        return ret_responses

def  exception_handler(request, exception):
    pass
    # exception_response = Response(None, request)
    # return request.callback(exception_response)
