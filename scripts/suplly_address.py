# encoding: utf-8

import os
import time
import json
import traceback
import requests
import multiprocessing

from multiprocessing import Manager, Queue
# from queue import Queue

import grequests
from logger import Logger
from settings import *

logger = Logger('supply_address').logger
BATCH_SIZE = 15
GAODE_KEY= ''

# task_queue = Queue()


def get_district_from_gaode(batch_items):
    def exception_handler(request, exception):
        try:
            raise exception
        except:
            logger.warning('[ERROR] {}'.format(traceback.format_exc()))
    batch_requests = []
    try:
        if not GAODE_KEY:
            logger.warning('GAODE_KEY is empty')
            exit(0)
        for item in batch_items:
            args = dict(
                url='http://restapi.amap.com/v3/geocode/geo',
                params={
                    'key': GAODE_KEY,
                    'address': item['workingAddress'],
                    'batch': 'true'
                }
            )
            batch_requests.append(grequests.get(**args))
        resps = grequests.map(batch_requests, exception_handler=exception_handler)
        for index, resp in enumerate(resps):
            province = district = city = ''
            if resp:
                resp = resp.json()
                if resp.get('count', 0) not in [0, "0"]:
                    province = resp['geocodes'][0]['province']
                    district = resp['geocodes'][0]['district']
                    city = resp['geocodes'][0]['city']
            batch_items[index]['province'] = province
            batch_items[index]['district'] = district
            batch_items[index]['city'] = city
    except:
        logger.error(traceback.format_exc())

def apply(task_queue, task_flag, num):
    def write_cache(f, batch_items):
        if batch_items:
            get_district_from_gaode(batch_items)
            for item in batch_items:
                f.write('{}\n'.format(json.dumps(item, ensure_ascii=False)))
        return []
    idle_count = 0
    process_name = 'process_{}'.format(num)
    cache_name = '{}_{}.cache'.format(task_flag, num)
    batch_items = []
    with open(os.path.join(CACHE_PATH, cache_name), 'w') as f:
        while True:
            try:
                line = task_queue.get(False)
                data = json.loads(line)
                if 'province' in data or 'district' in data or 'city' in data:
                    continue
            except Exception as e:
                time.sleep(0.5)
                idle_count += 1
                if idle_count == MAX_IDLE_TIMES:
                    write_cache(f, batch_items)
                    logger.info('{} finish.'.format(process_name))
                    break
            else:
                idle_count = 0
                batch_items.append(data)
                if len(batch_items) == BATCH_SIZE:
                    batch_items = write_cache(f, batch_items)

def read_data(task_queue):
    path = os.path.join(DATA_PATH, 'boss_tmp')
    with open(path, encoding='utf-8') as f:
        for line in f:
            task_queue.put(line)

def merge_cache(task_flag):
    caches = []
    for _, _, files in os.walk(CACHE_PATH):
        for f in files:
            if f.startswith(task_flag):
                caches.append(os.path.join(CACHE_PATH, f))
    if caches:
        with open(os.path.join(CACHE_PATH, 'boss_full'), 'w') as f:
            for cache_path in caches:
                with open(cache_path) as cache_f:
                    for line in cache_f:
                        f.write('{}\n'.format(line.strip()))
    logger.info('merge {} cache finish'.format(len(caches)))

def clean(task_flag):
    for _, _, files in os.walk(CACHE_PATH):
        for f in files:
            if f.startswith(task_flag):
                os.remove(os.path.join(CACHE_PATH, f))

def func(task_queue, task_flag=None, num=None):
    try:
        print('{}: {}'.format(num, task_queue.get(False)))
    except:
        pass

def main():
    # func()
    logger.info('started')
    manager = Manager()
    task_queue = manager.Queue()
    # task_queue = Queue()
    pool = multiprocessing.Pool(processes=5)
    read_data(task_queue)
    print(task_queue.qsize())
    # pool.apply_async(read_data)
    task_flag = str(int(time.time()*1000))
    for i in range(PROCESS_COUNT):
        pool.apply_async(func=apply, args=(task_queue, task_flag, i))
    pool.close()
    pool.join()
    merge_cache(task_flag)
    # clean(task_flag)
    logger.info('finished')


if __name__ == '__main__':
    main()