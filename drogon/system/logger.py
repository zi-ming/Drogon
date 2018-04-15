"""
    logger.py
    ~~~~~~~
    a logger module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import os
import logging
import logging.handlers

from drogon.settings import SYS_LOG_PATH, TASK_LOG_PATH

class Logger(object):
    def __init__(self, logger_name, log_file_path=TASK_LOG_PATH, is_rotating_file=False,
                 logging_format=None, max_bytes=0, backup_count=0):
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)
        if not logging_format:
            logging_format = "%(asctime)s - %(name)s - %(levelname)s:%(message)s"
        log_formatter = logging.Formatter(logging_format)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(log_formatter)
        logger.addHandler(sh)

        if log_file_path:
            path = os.path.join(log_file_path, '{}.log'.format(logger_name))
            if is_rotating_file:
                if not max_bytes:
                    max_bytes = 10*1024*1024
                if not backup_count:
                    backup_count = 5
                fh = logging.handlers.RotatingFileHandler(
                    path, maxBytes=max_bytes, backupCount=backup_count)
            else:
                fh = logging.FileHandler(path)
            fh.setLevel(logging.INFO)
            fh.setFormatter(log_formatter)
            logger.addHandler(fh)
        self.logger = logger

sys_logger = Logger('DROGON', log_file_path=SYS_LOG_PATH, is_rotating_file=True).logger

