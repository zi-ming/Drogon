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
import traceback

from requests.adapters import HTTPAdapter
import requests.exceptions as requests_ex
import requests.packages.urllib3.exceptions as urllib3_ex

from drogon.system.logger import sys_logger as logger
from drogon.system.downloader.base_downloader import BaseDownloader
from drogon.system.downloader.modules.response import Response
from drogon.settings import DEFAULT_HEADERS
from drogon.settings import MAX_REQUEST_RETRY
from drogon.system.downloader.proxy import handle_request_proxy
from drogon.system.scheduler.queue import CrawlStatus

requests.packages.urllib3.disable_warnings()

class RequestsDownloader(BaseDownloader):
    def __init__(self):
        self._retry_adapter = HTTPAdapter(max_retries=3)

    def download(self, batch):
        batch_requests = []
        for request in batch:
            session = requests.session()
            session.mount('http://', self._retry_adapter)
            session.mount('https://', self._retry_adapter)

            if not request.headers:
                request.headers = DEFAULT_HEADERS
            request = handle_request_proxy(request)
            args = dict(
                session=session,
                url=request.url,
                headers=request.headers,
                cookies=request.cookies,
                verify=False,
                allow_redirects=request.allow_redirects,
                timeout=request.timeout,
            )
            if request.meta.get('proxies', None):
                args['proxies'] = request.meta['proxies']
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
            CrawlStatus.increase(batch[index].spider_id)
            ret_responses.append(Response(
                response=ret,
                request=batch[index]
            ))
        return ret_responses

def  exception_handler(request, exception):
    try:
        raise exception
    except requests_ex.ProxyError:
        logger.warning('connection timeout: {}'.format(request.url))
    except requests_ex.ConnectionError:
        logger.warning('connection error: {}'.format(request.url))
    except RecursionError:
        logger.warning('RecursionError: maximum recursion depth exceeded: {}'.format(request.url))
    except:
        logger.warning(traceback.format_exc())
