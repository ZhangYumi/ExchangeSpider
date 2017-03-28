#-*- coding:utf-8 -*-
from scrapy.utils.project import get_project_settings
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from MyProject.items import SpiderItem
import urllib
import os
import re
import sys
import time


class SzseSpider(CrawlSpider):
    """
    深交所爬虫类
    """
    name = "szseSpider"
    baseUrl = "http://disclosure.szse.cn/"
    tag = u"深交所".encode('utf-8')
    allowed_domains = ["www.szse.cn"]
    bondUrl = "http://disclosure.szse.cn//disclosure/fulltext/plate/szbondlatest_1m.js"      #深交所债券公告返回数据
    latestUrl = "http://disclosure.szse.cn//disclosure/fulltext/plate/szlatest_24h.js"        #深交所最新上市公司公告
    settings = get_project_settings()
    basepath = settings['BASE_PATH']

    def start_requests(self):
        """
        为每个URL单独创建请求
        :return:
        """
        yield Request(url=self.bondUrl,callback=self.parse_bond)
        yield Request(url=self.latestUrl, callback=self.parse_latest)

    def parse_bond(self, response):
        """
        下载深交所债券公告，由于无法从返回页面直接解析，因此直接抓取js返回数据
        :param response:
        :return:
        """
        #aTitles = selector.xpath('//table[@class="ggnr"]/tbody/tr/td[@class="td2"]/a[@target="_blank"]/text()').extract()
        #aTimes = selector.xpath('//table[@class="ggnr"]/tbody/tr/td[@class="td2"]/span[@class="link1"]/text()').extract()
        #pdfUrls = selector.xpath('//table[@class="ggnr"]/tbody/tr/td[@class="td2"]/a[@target="_blank"]/@href').extract()

        aLists = response.body.split("],[")
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        announcementType = u"债券公告".encode('utf-8')
        length = len(aLists)
        output = sys.stdout
        for index,aList in enumerate(aLists):
            pdfUrl = aList.split(",")[1].strip('" ')
            pdfTitle = re.sub('[":?/*<>|\ ]','',aList.split(",")[2].strip('":?/*<>|\ ')).decode('gbk').encode('utf-8')        #正则去掉文件名中非法字符
            pdfTime = aList.split(",")[5].strip('" ')

            if pdfTime==today:
                relativeFilePath = "ExchangeSpider\\Data\\"+"{}\\{}\\{}\\".format(today,self.tag,announcementType)
                dirPath = unicode(self.basepath+relativeFilePath)
                savePath = unicode(dirPath + "{}.pdf".format(pdfTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.baseUrl + str(pdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=pdfTitle,
                        AnnouncementFrom=self.tag,
                        ReportingDate=today,
                        AnnouncementSort=announcementType,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(pdfTitle))
                    )
                    yield item
                except Exception:
                    print "Exception:",pdfTitle," ",pdfUrl
            process = '#'*int((index + 1) * 100.0 / length) + '='*int((length-index-1)*100.0/length)
            output.write("\r[%s] %s complete :" % (self.tag,announcementType) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print

    def parse_latest(self,response):
        aLists = response.body.split("],[")
        announcementType = u"最新上市公司公告".encode('utf-8')
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        length = len(aLists)
        output = sys.stdout
        for index, aList in enumerate(aLists):
            pdfUrl = aList.split(",")[1].strip('" ')
            pdfTitle = re.sub('[":?/*<>|\ ]','',aList.split(",")[2].strip('":?/*<>|\ ')).decode('gbk').encode('utf-8')            #正则去掉文件名中非法字符
            pdfTime = aList.split(",")[5].strip('" ')

            if pdfTime == today:
                relativeFilePath = "CCXR_Spider\\Data\\"+"{}\\{}\\{}\\".format(today,self.tag,announcementType)
                dirPath = unicode(self.basepath+relativeFilePath)
                savePath = unicode(dirPath + "{}.pdf".format(pdfTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.baseUrl + str(pdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=pdfTitle,
                        AnnouncementFrom=self.tag,
                        ReportingDate=today,
                        AnnouncementSort=announcementType,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(pdfTitle))
                    )
                    yield item
                except Exception:
                    print "Exception:",pdfTitle," ",pdfUrl
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :" % (self.tag,announcementType) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print
