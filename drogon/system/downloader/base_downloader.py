"""
    base_downloader.py
    ~~~~~~~
    the Base class of downloader
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-02
    :python version: 3.6
"""

class BaseDownloader(object):
    def downloader(self, request):
        raise NotImplementedError