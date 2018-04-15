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

from drogon.system.pipeline.base_pipeline import BasePipeline
from drogon.system.result import Result

class SaveRespPipeline(BasePipeline):
    def parse(self, response, spider):
        if response:
            result = Result(response, spider)
            self.parse_result(result, spider)

    def parse_result(self, result, spider):
        path = os.path.dirname(result.path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, result.result_id), 'w', encoding='utf-8') as f:
            f.write(result.text)