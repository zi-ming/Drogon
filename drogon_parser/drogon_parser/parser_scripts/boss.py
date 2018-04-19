
import re
import traceback

from lxml import etree

from drogon_parser.parser.base_parser import BaseParser
from drogon_parser.utils import clean_empty, check_need_dimensions, avg_value, handle_xpath_text
from drogon_parser.libs import parse_recruiting_salary, parse_working_seniority, \
    parse_recruiting_age_request, parse_member_count, get_district_from_gaode, \
    recognize_functions, parse_reg_capital, parse_recruiting_education

class Parser(BaseParser):
    parser_name = 'boss'

    def parse(self, content):
        if not content:
            return
        # 必要字段
        need_dimensions = ['entName', 'jobName', 'workingSalary', 'recruitingEducation',
                           'workingSeniority', 'recruitingAgeRequest', 'languageAbility',
                           'benefitList', 'industryList', 'recruitingMemberCount', 'workingProvince', 'functions']
        page_info, content = content.split('\n', 1)
        for feedback in self.parse_basic(content):
            if isinstance(feedback, dict):
                # 进一步清洗数据
                result = clean_empty(feedback)
                # 检查必要维度
                flag, lack_field = check_need_dimensions(result, need_dimensions)
                if flag:
                    yield result
                else:
                    self.logger.warning('[Filter] page_info:{}; lack_field:{}'.format(page_info, lack_field))

    def parse_basic(self, content):
        """
        清洗岗位基本信息
        :param content: html content
        :return:
        """
        result = dict()
        doc = etree.HTML(content)
        if not doc.xpath('//div[@class="about-position"]') or u'该职位已结束' in content:
            pass
            # self.logger.info('该职位已过期')
            return
        try:
            name = handle_xpath_text('//div[@class="title-info"]/h3//text()', doc).split(u'|')
            assert len(name) in [1, 2]
            if len(name) == 1 and len(name[0]):
                name = name[0]
            elif len(name) == 2 and len(name[1]):
                name = name[1]
            else:
                raise ValueError('未能识别的企业名')
            name = name.replace(u'看看其他高薪职位>>', u'').strip()
            assert name
        except:
            self.logger.error(traceback.format_exc())
            return
        # 企业名， 职位名，工资待遇
        result[u'entName'] = name
        result[u'jobName'] = handle_xpath_text('//div[@class="title-info"]/h1//text()', doc)
        result[u'workingSalary'] = handle_xpath_text('//p[@class="job-item-title"]/text()', doc)
        if u'面议' in result[u'workingSalary']:
            result[u'workingSalary'] = 0

        # 招聘学历要求、工作经验、岗位年龄要求
        result[u'recruitingEducation'] = handle_xpath_text('//div[@class="job-qualifications"]/span[1]/text()',
                                                           doc)
        result[u'workingSeniority'] = handle_xpath_text('//div[@class="job-qualifications"]/span[2]/text()',
                                                        doc)
        result[u'recruitingAgeRequest'] = handle_xpath_text('//div[@class="job-qualifications"]/span[4]/text()',
                                                            doc)
        # 语言能力要求，年龄要求
        if len(doc.xpath('//div[@class="job-qualifications"]/span')) == 4:
            txt = handle_xpath_text('//div[@class="job-qualifications"]/span[3]/text()',
                                    doc=doc, del_empty=True)
            result[u'languageAbility'] = txt.split(u'+')

        if u'不限' in result[u'recruitingAgeRequest']:
            result[u'recruitingAgeRequest'] = {'min': -1}
        # 岗位福利列表
        for span in doc.xpath('//div[@class="tag-list"]/span'):
            text = handle_xpath_text('./text()', doc=span)
            if text:
                result.setdefault(u'benefitList', [])
                result[u'benefitList'].append(text)
        # 职位描述、招聘企业简介
        desc = handle_xpath_text('//div[contains(@class, "job-description")]//text()', doc)
        if u'职位描述' in desc:
            result[u'recruitingDesc'] = handle_xpath_text('//div[@class="content content-word"]//text()',
                                                          doc=doc, del_empty=True)
        res = self.filter_ent_info(content)
        result.update(res)

        if u'workingSalary' in result:
            salary = parse_recruiting_salary(result[u'workingSalary'])
            if salary[u'coinType'] == u'人民币':
                result[u'workingSalary'] = avg_value(salary)
            else:
                result.pop(u'workingSalary')

        if u'workingSeniority' in result:
            result[u'workingSeniority'] = parse_working_seniority(result[u'workingSeniority'])
            result[u'workingSeniority'] = avg_value(result[u'workingSeniority'])

        if u'recruitingAgeRequest' in result:
            result['recruitingAgeRequest'] = parse_recruiting_age_request(result['recruitingAgeRequest'])
            result['recruitingAgeRequest'] = avg_value(result[u'recruitingAgeRequest'])

        if u'recruitingMemberCount' in result:
            result['recruitingMemberCount'] = parse_member_count(result['recruitingMemberCount'])
            result['recruitingMemberCount'] = avg_value(result[u'recruitingMemberCount'])

        if u'workingAddress' in result:
            result[u'workingProvince'], result[u'workingCity'], result[u'workingDistrict'] = \
                get_district_from_gaode(result[u'workingAddress'])
            result.pop(u'workingAddress')

        if u'recruitingDesc' in result:
            result['functions'] = recognize_functions(result[u'recruitingDesc'])
            result.pop(u'recruitingDesc')

        if u'regCapital' in result:
            capital = parse_reg_capital(result[u'regCapital'])
            if capital['coinType'] == '人民币':
                result[u'regCapital'] = capital['value']
            else:
                result.pop(u'regCapital')

        if u'recruitingEducation' in result:
            result[u'recruitingEducation'] = parse_recruiting_education(result[u'recruitingEducation'])
        yield result

    def filter_ent_info(self, content):
        """
        筛选出与企业相关的信息
        :param content: html content
        :return:
        """
        page_info, inner_content = content.split(u'\n', 1)
        doc = etree.HTML(inner_content)
        result = {
            u'industryList': [],
        }
        infos = doc.xpath('//ul[@class="new-compintro"]//li')
        for info in infos:
            txt = handle_xpath_text('.//text()', info)
            if u':' not in txt:
                continue
            values = txt.split(u':')
            k, v = values[0], values[-1]
            if any(map(lambda x: x in k, [u'行业', ])):
                v = re.sub(u'\(.*\)', u'', v)
                result[u'industryList'] += v.split(u'/')
            elif any(map(lambda x: x in k, [u'规模', ])):
                result[u'recruitingMemberCount'] = v
            elif any(map(lambda x: x in k, [u'地址', ])):
                result[u'workingAddress'] = v
        detail_infos = doc.xpath('//ul[@class="new-compdetail hide"]/li')
        for info in detail_infos:
            txt = handle_xpath_text('./text()', info)
            if u':' not in txt:
                continue
            try:
                k, v = txt.split(u':', 1)
            except:
                pass
            # if any(map(lambda x: x in k, [u'时间', ])):
            #     result[u'regTime'] = v
            if any(map(lambda x: x in k, [u'资本', ])):
                result[u'regCapital'] = re.sub(u'[\(\)]', u'', v)
            # if any(map(lambda x: x in k, [u'期限', ])):
            #     result[u'businessTerm'] = v
        position = handle_xpath_text('//input[@id="location"]/@value', doc).split(u',')
        if all(map(lambda x: re.match('[\d\.]+', x), position)):
            result[u'workLocation'] = {
                u'lat': position[1],
                u'lng': position[0]
            }
        if not result.get(u'workingAddress', u''):
            txt = handle_xpath_text('//p[@class="basic-infor"]/span/a/text()', doc)
            result[u'workingAddress'] = re.sub(u'-', u'', txt)
        return result