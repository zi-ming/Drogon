
class BaseSpider(object):
    spider_id = None
    spider_name = None

    spider_settings = dict(
        duplicate_remove=False,
        allow_redirects=False,
        ignore_error=True,
        use_proxy=False,
        timeout=60,
        priority=0,
    )

    start_requests = []
    start_url_file_path = None

    def parse(self, response):
        raise NotImplementedError