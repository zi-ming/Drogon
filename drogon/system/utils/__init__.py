
import os
import logging

if not os.path.exists('log'):
    os.mkdir('log')
logger = logging.getLogger('DROGON')
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s:%(message)s")

fh = logging.FileHandler('log/DROGON.log')
fh.setLevel(logging.INFO)
fh.setFormatter(log_formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(log_formatter)

logger.addHandler(fh)
logger.addHandler(sh)



