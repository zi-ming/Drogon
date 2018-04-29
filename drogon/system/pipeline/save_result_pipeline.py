"""
    save_resp_pipeline.py
    ~~~~~~~
    save results to local
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import os
from hashlib import md5

from drogon.system.pipeline.base_pipeline import BasePipeline
from drogon.system.result import Result
from drogon.settings import RESULT_PATH

class SaveResultPipeline(BasePipeline):
    def parse(self, result, spider):
        if result and isinstance(result, dict) and 'content' in result:
            path = result.get('path', '') or os.path.join(RESULT_PATH, spider.spider_id)
            if path and not os.path.exists(path):
                os.mkdir(path)
            result_id = md5(result['content'].encode('utf-8')).hexdigest()
            with open(os.path.join(path, result_id), 'w', encoding='utf-8') as f:
                f.write(result['content'])

    def parse_result(self, result, spider):
        path = os.path.dirname(result.path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, result.result_id), 'w', encoding='utf-8') as f:
            f.write(result.text)