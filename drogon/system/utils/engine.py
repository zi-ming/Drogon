
import os
from drogon.settings.default_settings import BASE_DIR

def read_start_urls_from_file(spider):
    root = os.path.join(os.path.dirname(BASE_DIR), 'start_urls')
    spider_dirname = os.path.join(root, spider.spider_id)
    if not os.path.exists(spider_dirname):
        raise IOError("No such file or directory: '%s'"%(spider_dirname))
    print(spider_dirname)
    for _, _, files in os.walk(spider_dirname):
        for f in sorted(files):
            with open(os.path.join(spider_dirname, f)) as f:
                for line in f:
                    yield line