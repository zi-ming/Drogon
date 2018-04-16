import os

SPIDER_PATH = os.getcwd()
BASE_PATH = os.path.dirname(SPIDER_PATH)
RESULT_PATH = os.path.join(BASE_PATH, os.path.join('output', 'sample'))
SYS_LOG_PATH = os.path.join(BASE_PATH, os.path.join('output', 'sys_log'))
TASK_LOG_PATH = os.path.join(BASE_PATH, os.path.join('output', 'task_log'))
START_URLS_PATH = os.path.join(BASE_PATH, 'start_urls')

PROXY_POOL_API = 'http://127.0.0.1:80'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
DB = 0

REQUEST_TIMEOUT = 60
MAX_REQUEST_RETRY = 3
REQUEST_BATCH_SIZE = 10
SPIDER_STOP_TIME = 1
IDLE_TIME = 1

LEGAL_STATUS_CODE = {200,}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Content-Type": "text/html;charset=utf-8",
    "Accept-Language":"zh-CN,zh;q=0.8"
}