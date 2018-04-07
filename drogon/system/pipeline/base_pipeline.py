
class BasePipeline(object):
    def parse(self, response, spider):
        raise NotImplementedError