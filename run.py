
from spiders.boss_spider import BossSpider
from drogon.system.spider.base_spider import BaseSpider
from drogon.system.engine.engine_core import EngineCore
from drogon.system.pipeline.save_resp_pipeline import SaveRespPipeline

engine = EngineCore(spider=BossSpider()).set_pipeline(SaveRespPipeline())
engine.start()