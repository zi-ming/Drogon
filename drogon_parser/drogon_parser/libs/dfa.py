# encoding: utf-8

from drogon_parser.settings import DFA_DICT_PATH

class DFA(object):

    """
    This class takes a file as parameter, and construct dfa structure
    for string parsing.
    """

    def __init__(self, file_name='dict.txt'):
        self._smap = self.__init_data(file_name)

    def __init_data(self, file_name):

        # read from file f and construct data structure
        smap = {}
        with open(DFA_DICT_PATH, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                line = line.lower()
                tmp = smap
                size = len(line)

                for i in range(size):
                    if line[i] in tmp:
                        tmp = tmp[line[i]]
                    else:
                        tmp[line[i]] = {'end': 0}
                        tmp = tmp[line[i]]

                    # check if the last character
                    if i == size - 1:
                        tmp['end'] = 1
        return smap

    def check_censor_word(self, i_string):
        """
        Return True when having sensitive word
        """
        string = i_string
        ret = set()
        for i, char in enumerate(string):
            if char in self._smap:

                for word in self.match_censor_word(string[i:]) or []:
                    if word is None:
                        continue
                    ret.add(word)
        return list(ret)

    def match_censor_word(self, sub_str):
        """
        Almost the same as check_censor_word other than it just match from the
        start of given string, if not matched, will not check other chars.

        :param sub_str:
        :return: A generator of matched word or None
        """
        string = sub_str
        word = u''
        tmp = self._smap
        flag = None
        for _, char in enumerate(string):
            if char in tmp:
                word = u'%s%s' % (word, char)
                tmp = tmp[char]
                # check if read the end
                if tmp['end'] == 1:
                    flag = word
        yield flag

    def match_censor_word_at_beginning(self, _str):
        """
        匹配一个字符串的开头

        :param _str:
        :return: A str or None
        """
        string = _str
        word = u''
        tmp = self._smap
        for _, char in enumerate(string):
            if char in tmp:
                word = u'%s%s' % (word, char)
                tmp = tmp[char]
            else:
                break
        if 'end' not in tmp or tmp['end'] != 1:
            word = ''
        return word

def export_words(txt):
    dfa = DFA()
    return dfa.check_censor_word(txt.lower())


if __name__ == '__main__':
    txt = '工作职能1、负责产品软件开发和维护;2、负责子系统或模块的概要设计和编码工作,主导分析解决系统级疑难问题;3、良好的问题分析、详细设计、代码调试、故障定位和解决能力。岗位要求:1、至少3年及以上软件开发经验,具备面向对象设计思想;2、精通C++,熟悉进程/线程技术、异步通信机制、内存管理、数据结构等;3、精通Linux/Windows环境下C++/STL/boost编程,熟悉linuxShell指令;4、熟悉Mysql/PostgreSQL数据库编程.Net5、熟悉socket网络编程,TCP/IP协议,有过服务器端开发经验者优先;6、熟悉网络存储产品,了解RAID、ISCSI、NAS协议优先考虑。7、两年以上分布式系统架构设计与开发经验,具有hadoop、hbase、spack等分布式系统开发经验者优先;您与该职位的匹配度?经验分布(年)学历分布登录查看职位竞争力分析'
    dfa = DFA()
    print(dfa.check_censor_word(txt))