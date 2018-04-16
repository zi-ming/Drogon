"""
    utils
    ~~~~~~~
    commonly used tools
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-16
    :python version: 3.6
"""

import time

get_date_time = lambda:time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
get_timestamp = lambda: int(time.time()*1000)