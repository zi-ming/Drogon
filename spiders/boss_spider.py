
from drogon.system.spider.base_spider import BaseSpider
from drogon.system.engine.engine_core import EngineCore
from drogon.system.pipeline.save_resp_pipeline import SaveRespPipeline

class BossSpider(BaseSpider):
    spider_id = 'boss_spider'
    MAX_RETRY_TIMES = 2

    def __init__(self):
        super(BossSpider, self).__init__(self.spider_id)
        url = 'https://www.zhipin.com/job_detail/1419070242.html?ka=search_list_1'
        self.start_requests = [self.fetch(url=url, meta={'use_proxy': False})]

    # def on_start(self, data):
    #     return self.fetch(url=data, meta={'use_proxy': True})

    def parse(self, response):
        if not response.response or response.response.status_code!=200:
            yield self.retry_get(response)
        else:
            self.logger.info('[SUCCESS] {}'.format(response.request.url))
            yield response

# engine = EngineCore(spider=BossSpider()).set_pipeline(SaveRespPipeline())
# engine.start()