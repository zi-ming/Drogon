import os

BASE_DIR = os.getcwd()
PROXY_PATH = os.path.join(BASE_DIR, 'proxies.txt')
MAX_REQUEST_RETRY = 3

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Content-Type": "text/html;charset=utf-8",
    "Accept-Language":"zh-CN,zh;q=0.8"
}
