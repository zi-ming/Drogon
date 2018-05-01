# encoding: utf-8
import os

BASE_PATH = os.getcwd()
SYS_LOG_PATH = os.path.join(BASE_PATH, 'log')
DATA_PATH = os.path.abspath(r'..\output\result\liepin_detail')
RESULT_PATH = os.path.abspath(r'..\output\result\full_liepin')
CACHE_PATH = os.path.abspath(r'..\output\result')

PROCESS_COUNT = 4
ASYN_COUNT = 15
MAX_IDLE_TIMES = 20