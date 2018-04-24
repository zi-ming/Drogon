# encoding: utf-8

import os
import time
import traceback
import requests
import multiprocessing
from queue import Queue

from logger import Logger
from settings import *

logger = Logger('supply_address').logger

task_queue = Queue(1000)


def get_district_from_gaode(address):
    '''
    利用高德接口提取所在区
    :param address:
    :return:
    '''
    args = dict(
        url='http://restapi.amap.com/v3/geocode/geo',
        params={
            'key': GAODE_KEY,
            'address': address,
            'batch': 'true'
        }
    )
    province, city, district = '', '', ''
    try:
        if not GAODE_KEY:
            logger.warning('GAODE_KEY is empty')
            return province, city, district
        resp = requests.get(**args)
        resp = resp.json()
        if resp.get('count', 0) not in [0, "0"]:
            district = resp['geocodes'][0]['district']
            province = resp['geocodes'][0]['province']
            city = resp['geocodes'][0]['city']
    except:
        logger.error(traceback.format_exc())
    return province, city, district


def apply(task_flag, num):
    idle_count = 0
    process_name = 'process_{}'.format(num)
    cache_name = '{}_{}.cache'.format(task_flag, num)
    with open(os.path.join(CACHE_PATH, cache_name), 'w') as f:
        while True:
            try:
                line = task_queue.get(False)
            except:
                time.sleep(0.5)
                idle_count += 1
                if idle_count == MAX_IDLE_TIMES:
                    logger.info('{} finish.'.format(process_name))
                    break
            else:
                idle_count = 0
                print('processing')
                time.sleep(5)

def read_data():
    with open(DATA_PATH) as f:
        for line in f:
            task_queue.put(line)

def clean(task_flag):
    for _, _, files in os.walk(CACHE_PATH):
        for f in files:
            if f.startswith(task_flag):
                os.remove(os.path.join(CACHE_PATH, f))

def func(i):
    print(i)

def main():
    logger.info('started')
    pool = multiprocessing.Pool()
    # pool.apply_async(read_data)
    task_flag = str(int(time.time()*1000))
    for i in range(4):
        pool.apply_async(func=apply, args=(task_flag, i))
    pool.close()
    pool.join()
    clean(task_flag)
    logger.info('finished')


if __name__ == '__main__':
    main()