
# from spiders.liepin_url_spider import LiePinUrlSpider as Spider
from spiders.liepin_detail_spider import Spider

from drogon.system.spider.base_spider import BaseSpider
from drogon.system.engine.engine_core import EngineCore
from drogon.system.pipeline.save_result_pipeline import SaveResultPipeline as Pipeline

engine = EngineCore(spider=Spider())
engine.start()