#-*- coding:utf-8 -*-
import os
import time
from scrapy.crawler import CrawlerProcess
from MyProject.spiders.sse_spiders import SseSpider
from MyProject.spiders.szse_spiders import SzseSpider
from MyProject.spiders.cninfo_spiders import CninfoSpider

today = time.strftime("%Y%m%d", time.localtime(int(time.time())))
savePath = "E:\\temp\\ccxrSpider_" + today + ".xlsx"

if os.path.exists(savePath):
    os.remove(savePath)
process = CrawlerProcess()
#process.crawl(SseSpider)
process.crawl(SzseSpider)
#process.crawl(CninfoSpider)
process.start() # the script will block here until all crawling jobs are finished
