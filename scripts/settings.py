# encoding: utf-8
import os

BASE_PATH = os.getcwd()
SYS_LOG_PATH = os.path.join(BASE_PATH, 'log')
DATA_PATH = os.path.abspath(r'..\output\result\boss')
RESULT_PATH = os.path.abspath(r'..\output\result\full_boss')
CACHE_PATH = os.path.abspath(r'..\output\result')

PROCESS_COUNT = 4
ASYN_COUNT = 5
MAX_IDLE_TIMES = 100