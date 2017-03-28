#-*- coding:utf-8 -*-
from scrapy.utils.project import get_project_settings
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from MyProject.items import SpiderItem
import urllib
import os
import sys
import time
import re
reload(sys)
sys.setdefaultencoding("utf-8")
class SseSpider(CrawlSpider):
    """
    上交所公告爬虫类
    """
    name = "sseSpider"
    tag = u"上交所".encode('utf-8')
    host = "http://www.sse.com.cn"
    allowed_domains = ["www.sse.com.cn"]
    settings = get_project_settings()
    basepath = settings['BASE_PATH']

    #由于不同的链接解析方式不同，因此自定义请求和解析函数
    def start_requests(self):
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/corporate/",callback=self.parse_common)        #企业债券公告
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/samprivate/", callback=self.parse_common)      # 中小企业私募债券
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/company/", callback=self.parse_common)          # 公司债券公告
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/exchangeable/", callback=self.parse_common)    # 可交换公司债券公告
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/npcorporate/", callback=self.parse_common)     # 非公开发行公司债券公告
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/subordinate/", callback=self.parse_common)     # 次级债券公告
        yield Request(url="http://www.sse.com.cn/disclosure/bond/announcement/asset/", callback=self.parse_common)            # 企业资产支持证券公告

        #由于可转换公司债券公告与可分离交易的可转换公司债券公告返回状态码304，无法从页面获取。因此找出两类公告js链接，单独发送请求。
        yield Request(url="http://www.sse.com.cn/js/common/detachableConvertibleBulletin/convertiblebulletin_new.js",callback=self.parse_convertible)  #可转换公司债券公告
        yield Request(url="http://www.sse.com.cn/js/common/detachableConvertibleBulletin/detachablebulletin_new.js",callback=self.parse_stoconvertible)  #分离交换的可转换公司债券公告

        #最新上市公司公告
        yield Request(url="http://www.sse.com.cn/disclosure/listedinfo/announcement/", callback=self.parse_latest)    #最新上市公告

    def parse_common(self,response):
        """
        解析债券公告信息,下载PDF文件
        :param response:
        :return:
        """
        selector = Selector(response)
        aSorts = selector.xpath('//div[@class="sse_common_wrap_cn"]/div[@class="sse_title_common"]/h2/text()').extract()  #债券公告类别
        aTimes = selector.xpath('//div[@class="sse_list_1"]/dl/dd/span/text()').extract()                                      #债券公告时间
        aTitles = selector.xpath('//div[@class="sse_list_1"]/dl/dd/a/text()').extract()                                         #债券公告标题
        #aUrls = selector.xpath('//ul[@class="dl-submenu"]/li[@class=""]/a[@target="_self"]/@href').extract()                #其他债券公告链接
        #usedUrl = selector.xpath('//ul[@class="dl-submenu"]/li[@class="active"]/a[@target="_self"]/@href').extract()       #当前打开的债券公告链接
        pdfUrls = selector.xpath('//div[@class="sse_list_1"]/dl/dd/a[@target="_blank"]/@href').extract()                     #PDF文档链接

        aSort = aSorts[0].encode('utf-8').strip()
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        relativeFilePath = "ExchangeSpider\\Data\\"+"{}\\{}\\{}\\".format(today, self.tag, aSort)
        dirPath = unicode(self.basepath+relativeFilePath)
        length = len(pdfUrls)
        output = sys.stdout
        for index,pdfUrl in enumerate(pdfUrls):
            if aTimes[index] == today:
                aTitle = re.sub('[":?/*<>|\ ]','',aTitles[index]).encode('utf-8').strip()
                savePath = unicode(dirPath + "{}.pdf".format(aTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.host + str(pdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=aTitle,
                        AnnouncementFrom = self.tag,
                        ReportingDate=today,
                        AnnouncementSort=aSort,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(aTitle))
                    )
                    yield item
                except Exception,e:
                    print e.message
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :"% (self.tag,aSort.strip()) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print

    def parse_convertible(self,response):
        aSort = u"可转换公司债券公告".encode('utf-8')
        aLists = response.body.split("_t.push(")
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        relativeFilePath = "CCXR_Spider\\Data\\"+"{}\\{}\\{}\\".format(today, self.tag, aSort)
        dirPath = unicode(self.basepath+relativeFilePath)
        length = len(aLists[1:])
        output = sys.stdout
        for index,aList in enumerate(aLists[1:]):
            aTitle = re.sub('[":?/*<>|\ ]','',aList.split(",")[0][7:].strip('":?/*<>|\ ')).encode('utf-8')        #正则去掉文件名中非法字符
            aTime =  aList.split(",")[1][5:].strip('" ')
            if index == length - 2:
                pdfUrl = (aList.split(",")[2][4:])[:-15:].strip('" ')
            else:
                pdfUrl = (aList.split(",")[2][4:])[:-4:].strip('" ')

            if aTime==today:
                savePath = unicode(dirPath + "{}.pdf".format(aTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.host + str(pdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=aTitle,
                        AnnouncementFrom=self.tag,
                        ReportingDate=today,
                        AnnouncementSort=aSort,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(aTitle))
                    )
                    yield item
                except Exception,e:
                    print e.message
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :" % (self.tag,aSort.strip()) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print

    def parse_stoconvertible(self,response):
        aSort = u"分离交换的可转换公司债券公告".encode('utf-8')
        aLists = response.body.split("_t.push(")
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        relativeFilePath = "CCXR_Spider\\Data\\"+"{}\\{}\\{}\\".format(today, self.tag, aSort)
        dirPath = unicode(self.basepath+relativeFilePath)
        length = len(aLists[1:])
        output = sys.stdout
        for index,aList in enumerate(aLists[1:]):
            aTitle = re.sub('[":?/*<>|\ ]','',aList.split(",")[0][7:].strip('":?/*<>|\ ')).encode('utf-8')              #正则去掉文件名中非法字符
            aTime =  aList.split(",")[1][5:].strip('" ')
            if index == length - 2:
                pdfUrl = (aList.split(",")[2][4:])[:-15:].strip('" ')
            else:
                pdfUrl = (aList.split(",")[2][4:])[:-4:].strip('" ')

            if aTime==today:
                savePath = unicode(dirPath + "{}.pdf".format(aTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.host + str(pdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=aTitle,
                        AnnouncementFrom=self.tag,
                        ReportingDate=today,
                        AnnouncementSort=aSort,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(aTitle))
                    )
                    yield item
                except Exception,e:
                    print e.message
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :" % (self.tag,aSort.strip()) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print

    def parse_latest(self, response):
        """
        解析最新公告页面，下载最新公告PDF文件
        :param response:
        :return:
        """
        selector = Selector(response)
        lSorts = selector.xpath('//div[@class="sse_title_common"]/h2/text()').extract()
        lTimes = selector.xpath('//dl[@class="modal_pdf_list"]/dd[@class="just_this_only"]/span/text()').extract()
        lTitles = selector.xpath('//dl[@class="modal_pdf_list"]/dd[@class="just_this_only"]/em[@class="pdf-first"]/@title').extract()
        lPdfUrls = selector.xpath('//dl[@class="modal_pdf_list"]/dd[@class="just_this_only"]/em[@class="pdf-first"]/a[@target="_blank"]/@href').extract()

        lSort = lSorts[0].encode('utf-8').strip()
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        relativeFilePath = "CCXR_Spider\\Data\\"+"{}\\{}\\{}\\".format(today, self.tag, lSort)
        dirPath = unicode(self.basepath+relativeFilePath)
        length = len(lPdfUrls)
        output = sys.stdout
        for index, lPdfUrl in enumerate(lPdfUrls):
            if lTimes[index] == today:
                lTime = lTimes[index].strip()
                lTitle = re.sub('[":?/*<>|\ ]','',lTitles[index].strip())        #正则去掉文件名中非法字符
                savePath = unicode(dirPath + "{}.pdf".format(lTitle))
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                try:
                    urllib.urlretrieve(self.host + str(lPdfUrl), savePath)
                    item = SpiderItem(
                        AnnouncementTitle=lTitle,
                        AnnouncementFrom=self.tag,
                        ReportingDate=today,
                        AnnouncementSort=lSort,
                        AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(lTitle))
                    )
                    yield item
                except Exception,e:
                    print e.message
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :" % (self.tag,lSort.strip()) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print
