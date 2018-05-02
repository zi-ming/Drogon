# encoding: utf-8

import json
from drogon.system.spider.base_spider import BaseSpider

class Spider(BaseSpider):
    spider_id = 'liepin_detail'
    MAX_RETRY_TIMES = 5

    def __init__(self):
        super(Spider, self).__init__(self.spider_id)
        # task_msg = '{"url": "https://www.liepin.com/job/1913177651.shtml", "province_name": "安徽省", "city_code": "080040", "city_name": "蚌埠", "province_code": "080"}'
        # task_data = json.loads(task_msg)
        # meta = {
        #     'use_proxy': True,
        #     'task_msg': task_msg,
        #     'task_data': task_data
        # }
        # self.start_requests = [self.fetch(url=task_data['url'], meta=meta)]

    def on_start(self, task_msg):
        if not task_msg:
            return
        self.logger.info('[RECEIVED] {}'.format(task_msg))
        task_data = json.loads(task_msg)
        meta = {
            'use_proxy': True,
            'task_msg': task_msg,
            'task_data': task_data
        }
        yield self.fetch(url=task_data['url'], meta=meta)

    def parse(self, response):
        try:
            assert response and response.response.status_code < 300
            assert self.ensure_liepin(response)
            meta = response.request.meta
            page_mark = meta['task_msg']
            result = {
                'content': '{}\n{}'.format(page_mark, response.response.text)
            }
            yield result
            self.logger.info('[SUCCESS] {}'.format(response.request.url))
        except:
            yield self.retry_get(response)

    def ensure_liepin(self, response):
        return 'www.liepin.com' in response.response.text

