"""
    base_pipeline.py
    ~~~~~~~
    the Base class of pipeline
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

class BasePipeline(object):
    def parse(self, response, spider):
        raise NotImplementedError