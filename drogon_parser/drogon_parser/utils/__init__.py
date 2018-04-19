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
import re
from lxml import etree
from copy import deepcopy

get_date_time = lambda:time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
get_timestamp = lambda: int(time.time()*1000)

def strQ2B(ustring):
    """全角转半角"""
    r_string = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif 65281 <= inside_code <= 65374:  # 全角字符（除空格）根据关系转化
            inside_code -= 65248
        r_string += chr(inside_code)
    return r_string

def clean_empty(result, exclusive=[]):
    if not isinstance(result, dict):
        raise ValueError('result must be dict object')
    inner_result = deepcopy(result)
    for k, v in result.items():
        if k in exclusive:
            continue
        if isinstance(v, (int, float, bool)):
            continue
        if isinstance(v, str) and not v.strip():
            inner_result.pop(k)
            continue
        if not v:
            inner_result.pop(k)
            continue
    return inner_result

def check_need_dimensions(result, dimensions):
    if not isinstance(result, dict):
        raise ValueError('result must be dict object')
    for field in dimensions:
        if field not in result:
            return False, field
    return True, None

def avg_value(dict_obj):
    if not isinstance(dict_obj, dict):
        raise ValueError('type must be dict object')
    min = max = None
    if 'min' in dict_obj:
        min = float(dict_obj['min'])
    if 'max' in dict_obj:
        max = float(dict_obj['max'])
    if min is None and max is None:
        return None
    if min is None:
        return max
    if max is None:
        return min
    return (min + max)/2

def handle_xpath_text(parten, doc=None, content=None, del_empty=False):
    if doc is None and content is None:
        raise ValueError('both doc and content must not be None')
    if not doc:
        doc = etree.HTML(content)
    txt = u''.join(doc.xpath(parten)).strip()
    txt = strQ2B(txt)
    txt = re.sub(u'\s', u'', txt) if del_empty else txt
    return txt