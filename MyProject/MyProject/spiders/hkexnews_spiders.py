#-*- coding:utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from MyProject.items import SpiderItem
import urllib
import os
import re
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

class HkexnewsSpider(CrawlSpider):
    """
    港交所爬虫类
    """
    name = "hkexnewsSpider"
    allowed_domains = ["www.hkexnews.hk"]
    start_urls = ["http://www.hkexnews.hk/listedco/listconews/mainindex/SEHK_LISTEDCO_DATETIME_TODAY_C.HTM"]

    def parse(self, response):
        """
        港交所最新上市公司公告页面解析
        """
        selector = Selector(response)
        selector.xpath('\\tbody\tr[@class="row0"]')
