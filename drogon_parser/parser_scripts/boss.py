
from drogon_parser.parser.base_parser import BaseParser

class Parser(BaseParser):
    parser_name = 'boss'

    def parse(self, content):
        print(len(content))