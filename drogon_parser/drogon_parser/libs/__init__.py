
import time
import re
import requests

from drogon_parser.utils import strQ2B
from drogon_parser.libs.dfa import export_words
from drogon_parser.settings import GAODE_KEY

def parse_recruiting_salary(value):
    """
    提取薪资
    """
    if isinstance(value, dict):
        return value
    value = re.sub('[\s]', '', str(value))
    coin_type = re.search(u'(美|日元|港)', value)
    if not value:
        return None
    new_value = {}
    reg = u'(\d+\.+\d+|\d+)(千|万|元|w|k|K)?[-~]?(\d+\.+\d+|\d+)?' + \
                  u'(千|万|元|w|k|K)?(以上|\+|及以上)?(以下)?[\/]?(月|年|天|小时)?'
    match = re.match(reg, value)
    if not match:
        return None
    min_v, e_unit, max_v, unit, more, less, per = match.groups()
    # 处理单位
    rate = 1
    if unit:
        if unit == u'万' or unit == u'w':
            rate = 10000
        elif unit in (u'k', u'K', u'千'):
            rate = 1000
    elif e_unit:
        if e_unit in (u'k', 'K', u'千'):
            rate = 1000
        elif e_unit == u'w' or e_unit == u'万':
            rate = 10000
    # 资金数
    if min_v and max_v:
        new_value[u'max'] = float(max_v) * rate
        new_value[u'min'] = float(min_v) * rate
    elif min_v and not max_v and not more and not less:
        new_value[u'max'] = float(min_v) * rate
        new_value[u'min'] = float(min_v) * rate
    elif min_v and not max_v and more:
        new_value[u'min'] = float(min_v) * rate
    elif min_v and not max_v and less:
        new_value[u'max'] = float(min_v) * rate
    # 资金单位
    if coin_type:
        coin_type = coin_type.group()
        if coin_type == u'美':
            new_value[u'coinType'] = u'美元'
        elif coin_type == u'日':
            new_value[u'coinType'] = u'日元'
        elif coin_type == u'港':
            new_value[u'coinType'] = u'港元'
    else:
        new_value[u'coinType'] = u'人民币'
    # 时间单位
    if per == u'年':
        new_value[u'period'] = u'year'
    elif per == u'月':
        new_value[u'period'] = u'month'
    elif per == u'天':
        new_value[u'period'] = u'day'
    elif per == u'小时':
        new_value[u'period'] = u'hour'
    return new_value

def parse_working_seniority(value):
    """
    提取工作经验
    """
    if isinstance(value, dict):
        return value
    value = re.sub(u'未填', '', value)
    if value:
        match = re.match(u'(?:经验)?(\d+)[-~]?(\d+)?年?(以上)?(以下)?', value)
        if re.match(u'.*不限|应届.*|在读.*|无工作.*', value):
            value = {
                'max': 0,
                'min': 0
            }
            return value
        elif match:
            min_v, max_v, more, less = match.groups()
            if min_v and max_v:
                value = {
                    'max': int(max_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and not more and not less:
                value = {
                    'max': int(min_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and more:
                value = {
                    'min': int(min_v)
                }
            elif min_v and not max_v and less:
                value = {
                    'max': int(min_v)
                }
            return value
    return None

def parse_recruiting_age_request(value):
    """
    提取年龄要求
    """
    if isinstance(value, str):
        match = re.match(u'(少于)?(\d+)[-~到]?(\d+)?岁?(以上)?(以下)?', value)
        if match:
            less_1, min_v, max_v, more, less_2 = match.groups()
            if min_v and max_v:
                value = {
                    'max': int(max_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and not more and not less_2:
                value = {
                    'max': int(min_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and more:
                value = {
                    'min': int(min_v)
                }
            elif min_v and not max_v and less_2:
                value = {
                    'max': int(min_v)
                }
            elif less_1 and min_v:
                value = {
                    'max': int(min_v)
                }
            else:
                return None
    elif isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(v, int):
                value[k] = int(v)
    if isinstance(value, dict) and 'min' in value and value['min'] - 0 == 0:
        return None
    if isinstance(value, dict) and 'max' in value and value['max'] - 0 == 0:
        return None
    return value

def parse_member_count(value):
    """
    提取人员数量
    """
    if isinstance(value, str):
        value = re.sub('[\s]', '', value)
        match = re.match(u'(少于)?(\d+)[-~]?(\d+)?人?(以上)?(以下)?', value)
        if match:
            less_1, min_v, max_v, more, less_2 = match.groups()
            if min_v and max_v:
                value = {
                    'max': int(max_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and not more and not less_2:
                value = {
                    'max': int(min_v),
                    'min': int(min_v)
                }
            elif min_v and not max_v and more:
                value = {
                    'min': int(min_v)
                }
            elif min_v and not max_v and less_2:
                value = {
                    'max': int(min_v)
                }
            elif less_1 and min_v:
                value = {
                    'max': int(min_v)
                }
        else:
            return None
    elif isinstance(value, dict):
        for k, v in value.iteritems():
            if not isinstance(v, int):
                value[k] = int(v)
    if isinstance(value, dict) and 'min' in value and value['min'] - 0 == 0:
        return None
    if isinstance(value, dict) and 'max' in value and value['max'] - 0 == 0:
        return None

    return value

def transform_number(value):
    """: 把中文数字转换成英文数字
    @param value: 需要转换的数据
    @return value: 转换后的数据
    """
    zn_numbers = u'０１２３４５６７８９'
    en_numbers = '0123456789'

    def repl(matched):
        """: 替换规则"""
        zn_number = matched.group(0)
        zn_index = zn_numbers.find(zn_number)
        return en_numbers[zn_index]
    value = re.sub(u'[%s]' % zn_numbers, repl, value)
    return value

def parse_reg_time(value):
    '''
    提取注册时间
    :param value:
    :return:
    '''
    value = value
    value = transform_number(value)
    value = value.strip()
    value = re.sub(u'年|月', '-', value)
    value = re.sub(u'[日-]$', '', value)
    try:
        if int(value[0:4]) > time.localtime()[0] or int(value[0:4]) < 1860:
            return None
    except:
        return None

    if re.match('^[0-9]+$', value):
        if len(value) == 8:
            return value[0:4] + '-' + value[4:6] + '-' + value[6:8]
        elif len(value) == 6:
            if int(value[4:6]) < 12:
                return value[0:4] + '-' + value[4:6]
            else:
                return value[0:4] + '-0' + value[4:5] + '-0' + value[5:6]
    else:
        match = re.match(
            u'([0-9]{4})[^0-9]?([0-9]{1,2})?[^0-9]?([0-9]{1,2})?(.*)?', value)
        if match:
            year, month, day, other = match.groups()
            value = year
            if month:
                if int(month) > 12 or int(month) < 1:
                    return None
                if len(month) == 1:
                    month = '0%s' % month
                value += '-' + month
            if day:
                if int(day) > 31 or int(day) < 1:
                    return None
                if len(day) == 1:
                    day = '0%s' % day
                value += '-' + day
    return value

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
    resp = requests.get(**args)
    resp = resp.json()
    province, city, district = '', '', ''
    if resp.get('count', 0) not in [0, "0"]:
        district = resp['geocodes'][0]['district']
        province = resp['geocodes'][0]['province']
        city = resp['geocodes'][0]['city']
    return province, city, district

def recognize_functions(txt):
    return export_words(txt)

def parse_reg_capital(value):
    if isinstance(value, str):
        if not re.search('\d', value):
            return None

        def repl(matched):
            """: 替换规则"""
            return u'万元' + matched.group(1)
        value = strQ2B(value).replace(u'\u3000', u'')
        value = re.sub(u'\s', u'', value).replace(u'\u3000', u'')
        value = value.replace(u'香港元', u'港币')
        value = re.sub(u'万元(美元|人民币|港元|新加坡元|港币)', repl, value)
        value = re.sub(u'￥|人民币元|元人民币|RMB|\(元\)', u'人民币', value)
        value = value.replace(u'万元', u'万')
        value = value.replace(u'USD', u'美元')
        value = re.sub(r' |,|\\xa|整|以下|以上', '', value)
        match_1 = re.match(u'([0-9\.]+)(万|亿)?(人民币|美元|欧元|日元|港币)?', value)
        match_2 = re.match(u'(人民币|美元|欧元|日元|港币)([0-9\.]+)(万)', value)
        match_3 = re.match(
            u'([0-9\.]+)(万)[-~]([0-9\.]+)(万)(人民币|美元|欧元|日元|港币)?', value)
        v = unit = coin_type = None
        if match_1:
            v, unit, coin_type = match_1.groups()
        elif match_2:
            coin_type, v, unit = match_2.groups()
        elif match_3:
            v = match_3.group(3)
            unit = match_3.group(4)
            coin_type = match_3.group(5)
        if v and unit and coin_type:
            unit = 10000 if unit == u'万' else 100000000
            value = {
                'value': float(v) * unit,
                'coinType': coin_type
            }
        elif v and unit and not coin_type:
            unit = 10000 if unit == u'万' else 100000000
            value = {
                'value': float(v) * unit,
                'coinType': u'人民币'
            }
        elif v and unit is None and coin_type:
            value = {
                'value': float(v),
                'coinType': coin_type
            }
        elif v and unit is None and not coin_type:
            value = {
                'value': float(v),
                'coinType': u'人民币'
            }
        else:
            return None
    if isinstance(value, dict) and value.get('value', -1) < 0:
        return None
    return value

def parse_recruiting_education(value):
    educations = [u'不限', u'中专', u'中技', u'初中', u'博士', u'大专', u'本科', u'硕士', u'高中']
    for item in educations:
        if item in value:
            return item
    else:
        return None
