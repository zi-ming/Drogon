# encoding: utf-8
import re
import os
import traceback
import json

from copy import deepcopy
from lxml import etree
from drogon.system.spider.base_spider import BaseSpider

class Spider(BaseSpider):
    spider_id = 'liepin_url'

    MAX_RETRY_TIMES = 5

    base_url = 'https://www.liepin.com'
    page_url = 'https://www.liepin.com/zhaopin/?fromSearchBtn=2&degradeFlag=0&init=-1&dqs={}&key=%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91&d_pageSize=40&d_sfrom=search_unknown&d_curPage=0&curPage={}'

    def __init__(self):
        super(Spider, self).__init__(self.spider_id)
        # msg = '050	广东省	050020	广州'
        # info = msg.split('\t')
        # url = self.page_url.format(info[2], 0)
        # meta = {
        #     'use_proxy': True,
        #     'province_code': info[0],
        #     'province_name': info[1],
        #     'city_code': info[2],
        #     'city_name': info[3],
        #     'task_url': url,
        #     'cur_page': 0,
        #     'task_msg': msg
        # }
        # self.start_requests = [self.fetch(url=url, meta=meta)]

    def on_start(self, task_msg):
        if not task_msg:
            return
        self.logger.info('[RECEIVED] {}'.format(task_msg))
        info = task_msg.split('\t')
        url = self.page_url.format(info[2], 0)
        meta = {
            'use_proxy': True,
            'province_code': info[0],
            'province_name': info[1],
            'city_code': info[2],
            'city_name': info[3],
            'task_url': url,
            'cur_page': 0,
            'task_msg': task_msg
        }
        yield self.fetch(url=url, meta=meta)

    def parse(self, response):
        try:
            request = response.request
            _response = response.response
            assert _response and _response.status_code < 300
            assert self.ensure_liepin(_response)
            meta = request.meta
            doc = etree.HTML(_response.text)
            last_url = doc.xpath('//div[@class="pagerbar"]/a[last()]/@href')
            if not last_url:
                last_num = 1
            else:
                last_num = int(re.search('&curPage=(\d+)', last_url[0]).group(1)) + 1
            self.logger.info('[TOTAL-PAGE] {} {}'.format(meta['city_name'], last_num))
            self.save_content(response)
        except Exception as e:
            if not isinstance(e, AssertionError):
                if isinstance(e, IndexError):
                    self.logger.error('[EXCEPTION] {} {}'.format(last_url, str(traceback.format_exc())))
                else:
                    self.logger.error('[EXCEPTION] {}'.format(str(traceback.format_exc())))
            yield self.retry_get(response)
        else:
            self.logger.info('[SUCCESS] {}'.format(meta['task_url']))
            for page in range(1, last_num):
                url = self.page_url.format(meta['city_code'], page)
                self.logger.info('[RECEIVED] {}'.format(url))
                _meta = deepcopy(meta)
                _meta.update({
                    'cur_page': page,
                    'task_url': url
                })
                yield self.fetch(
                    url=url,
                    callback=self.parse_next_page,
                    meta=_meta
                )

    def parse_next_page(self, response):
        try:
            request = response.request
            _response = response.response
            assert _response and _response.status_code < 300
            assert self.ensure_liepin(_response)
            meta = request.meta
            self.save_content(response)
        except Exception as e:
            if not isinstance(e, AssertionError):
                self.logger.error('[EXCEPTION] {}'.format(str(traceback.format_exc())))
            yield self.retry_get(response)
        else:
            self.logger.info('[SUCCESS] {}'.format(meta['task_url']))

    def save_content(self, response):
        meta = response.request.meta
        doc = etree.HTML(response.response.text)
        job_urls = doc.xpath('//div[@class="job-info"]/h3/a[1]/@href')
        path = '/home/zm/code/Drogon/start_urls/liepin_detail/'
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, 'job_urls.txt')
        with open(path, 'a', encoding='utf-8') as f:
            for url in job_urls:
                if 'job' not in url:
                    continue
                if url.startswith('/'):
                    url = self.base_url + url
                line = {
                    'province_name': meta['province_name'],
                    'province_code': meta['province_code'],
                    'city_name': meta['city_name'],
                    'city_code': meta['city_code'],
                    'url': url,
                    'page': meta['cur_page']
                }
                f.write('{}\n'.format(json.dumps(line, ensure_ascii=False)))

    def ensure_liepin(self, response):
        try:
            doc = etree.HTML(response.text)
            href = doc.xpath('//a[@class="logo-link"]/@href')
            if not href:
                href = doc.xpath('//div[@class="logo"]/a[1]/@href')
            if href[0] == 'https://www.liepin.com/':
                return True
        except:
            self.logger.error('[EXCEPTION] {}'.format(str(traceback.format_exc())))
        return False


