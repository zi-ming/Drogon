
from spiders.liepin_url_spider import Spider
# from spiders.liepin_detail_spider import Spider

from drogon.system.engine.engine_core import EngineCore

engine = EngineCore(spider=Spider())
engine.start()
