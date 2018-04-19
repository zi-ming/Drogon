
import os

BASE_PATH = os.getcwd()
OUTPUT_PATH = os.path.join(os.path.dirname(BASE_PATH), 'output')
SAMPLE_PATH = os.path.join(OUTPUT_PATH, 'sample')
RESULT_PATH = os.path.join(OUTPUT_PATH, 'result')
SYS_LOG_PATH = os.path.join(OUTPUT_PATH, 'sys_log')
TASK_LOG_PATH = os.path.join(OUTPUT_PATH, 'task_log')
DFA_DICT_PATH = os.path.join(BASE_PATH, 'drogon_parser/libs/dict.txt')

GAODE_KEY = '0000'