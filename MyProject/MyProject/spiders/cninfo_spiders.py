#-*- coding:utf-8 -*-
from scrapy.utils.project import get_project_settings
from scrapy.spiders import CrawlSpider
from scrapy.http import FormRequest
from MyProject.items import SpiderItem
import urllib
import os
import re
import sys
import time
import json
import requests

class CninfoSpider(CrawlSpider):
    """
    巨潮资讯网爬虫类
    """
    name = "cninfoSpider"
    tag = u"巨潮资讯网".encode('utf-8')
    host = "http://www.cninfo.com.cn/"
    allowed_domains = ["www.cninfo.com.cn"]
    settings = get_project_settings()
    basepath = settings['BASE_PATH']
    def start_requests(self):
        """
        为每一个机构构造自己的post请求
        :return:
        """
        #深交所post请求
        yield FormRequest(url = "http://www.cninfo.com.cn/cninfo-new/disclosure/regulator_szse_latest",formdata={
        "column" : "regulator_szse",
        "tabName" : "latest"
    },callback=self.parse)

        #上交所post请求
        yield FormRequest(url = "http://www.cninfo.com.cn/cninfo-new/disclosure/regulator_sse_latest",formdata={
        "column" : "regulator_sse",
        "tabName" : "latest"
    },callback=self.parse)
        #结算公司post请求
        yield FormRequest(url="http://www.cninfo.com.cn/cninfo-new/disclosure/regulator_jsgs_latest", formdata={
            "column": "regulator_jsgs",
            "tabName": "latest"
        }, callback=self.parse)
        #证监会post请求
        yield FormRequest(url="http://www.cninfo.com.cn/cninfo-new/disclosure/regulator_zjh_latest", formdata={
            "column": "regulator_zjh",
            "tabName": "latest"
        }, callback=self.parse)

    def parse(self,response):
        """
        Ajax返回数据解析
        """
        jsonObjs = json.loads(response.text)['announcements']
        length = len(jsonObjs)
        output = sys.stdout
        today = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
        aSort = u"监管机构公告".encode('utf-8')
        relativeFilePath = "ExchangeSpider\\Data\\"+"{}\\{}\\{}\\".format(today, self.tag, aSort)
        dirPath = unicode(self.basepath+relativeFilePath)
        for index,jsonObj in enumerate(jsonObjs):
            announcementTitle = re.sub('[":?/*<>|\ ]','',jsonObj['announcementTitle']).encode('utf-8')        #去除文件名中的非法字符,转换编码
            adjunctUrl = jsonObj['adjunctUrl']                                                                 #公告链接
            #print jsonObj['announcementTime'],time.time()
            announcementTime = time.strftime("%Y-%m-%d",time.localtime(int(int(jsonObj['announcementTime'])*0.001)))        #格式化时间戳

            adjunctType = jsonObj['adjunctType']
            if today == announcementTime:
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                if adjunctType == "PDF":
                    try:
                        savePath = unicode(dirPath + "{}.pdf".format(announcementTitle))
                        urllib.urlretrieve(self.host+str(adjunctUrl),savePath)
                        item = SpiderItem(
                            AnnouncementTitle=announcementTitle,
                            AnnouncementFrom=self.tag,
                            ReportingDate=today,
                            AnnouncementSort=aSort,
                            AnnouncementPath=unicode(relativeFilePath+"{}.pdf".format(announcementTitle))
                        )
                        yield item
                    except Exception:
                        print "Exception:", announcementTitle, " ", adjunctUrl
                if adjunctType == "TXT":
                    try:
                        url = self.host+str(adjunctUrl)
                        html = requests.get(url)
                        list0 = re.findall(r'(?<=\[).*?(?=\])', html.text)
                        content = json.loads(list0[0])
                        contentTitle = re.sub('[":?/*<>|\ ]','',content['Title']).encode('utf-8')
                        contentZw = content['Zw'].encode('utf-8')
                        savePath = unicode(dirPath + "{}.html".format(contentTitle))
                        with open(savePath,'wb') as fs:
                            fs.write(contentZw)
                            item = SpiderItem(
                                AnnouncementTitle=announcementTitle,
                                AnnouncementFrom=self.tag,
                                ReportingDate=today,
                                AnnouncementSort=aSort,
                                AnnouncementPath=unicode(relativeFilePath+"{}.html".format(contentTitle))
                            )
                            yield item
                    except Exception:
                        pass
            process = '#' * int((index + 1) * 100.0 / length) + '=' * int((length - index - 1) * 100.0 / length)
            output.write("\r[%s] %s complete :" % (self.tag,aSort) + process + "%.0f%%" % int((index + 1) * 100.0 / length))
            output.flush()
        print






