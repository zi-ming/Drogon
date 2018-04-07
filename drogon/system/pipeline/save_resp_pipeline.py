
import os

from drogon.system.pipeline.base_pipeline import BasePipeline
from drogon.system.result import Result

class SaveRespPipeline(BasePipeline):
    def parse(self, response, spider):
        result = Result(response, spider)
        self.parse_result(result, spider)

    def parse_result(self, result, spider):
        path = os.path.dirname(result.path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, result.result_id), 'w', encoding='utf-8') as f:
            f.write(result.text)