# -*- coding: utf-8 -*-
import csv

import scrapy
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.http.request.form import Request


class LianjiaHouseSpider(Spider):
    name = 'lianjia_house'
    allowed_domains = ['bj.lianjia.com']
    # start_urls = ['http://bj.lianjia.com/']

    start_urls = ['https://bj.lianjia.com/xiaoqu/chaoyang/']
    furl = "https://bj.lianjia.com"
    districts = ["dongcheng", "haidian", "fengtai", "tongzhou", "changping", "daxing", "shunyi"]
    columns = ["district", "area", "name", "price", "lon", "lat"]

    # with open("C:\\Users\\Administrator\\Desktop\\lbs\\house_price.csv", 'w') as csvfile:
    csvfile = open("C:\\Users\\Administrator\\Desktop\\lbs\\house_price.csv", 'w')
    writer = csv.writer(csvfile)
    writer.writerow(columns)

    def __init__(self):
        super(LianjiaHouseSpider, self).__init__()

        for district in self.districts:
            self.start_urls.append('%s/xiaoqu/%s/' % (self.furl, district))

    # def parse(self, response):
    #     sel = Selector(response)
    #     ll = sel.xpath('//div[@data-role="ershoufang"]/div[2]/a/@href').extract()
    #
    #     for xiaoqu in ll:
    #         url = '%s%s' % (self.furl, xiaoqu)
    #         print("parse", url)
    #         yield Request(
    #             url=url,
    #             method='GET',
    #             callback=self.parse2
    #         )

    def parse(self, response):
        sel = Selector(response)
        ll = sel.xpath('//div[@data-role="ershoufang"]/div[2]/a/@href').extract()

        for xiaoqu in ll[1:]:
            url = '%s%s' % (self.furl, xiaoqu)
            print("parse2", url)
            yield Request(
                url=url,
                method='GET',
                callback=self.parse3
            )

    def parse3(self, response):
        sel = Selector(response)
        p = sel.xpath('//div/@page-data').re('"totalPage":\d+')[0][(len("totalPage") + 3):]
        for i in range(1, int(p) + 1):
            url = '%s%s/' % (response.url, 'pg%d' % i)
            print("parse3", url)
            yield Request(
                url=url,
                method='GET',
                callback=self.parse4
            )

    def parse4(self, response):
        sel = Selector(response)
        l1 = sel.xpath('//ul[@class="listContent"]/li[@class="clear xiaoquListItem"]')
        urls = l1.xpath('//div[@class="title"]/a/@href').extract()
        for surl in urls:
            print("parse4", surl)
            yield Request(
                url=surl,
                method='GET',
                callback=self.sub_parse
            )

    def sub_parse(self, response):
        sel = Selector(response)
        name = sel.xpath('//h1[@class="detailTitle"]/text()').extract()[0]
        try:
            price = sel.xpath('/html/body/div[6]/div[2]/div[1]/div/span[1]/text()').extract()[0]
        except Exception as e:
            price = 0
            # print(e)
        lat_lon = sel.xpath('//script[@type="text/javascript"]/text()').re('(\d+.\d+,\d+.\d+)')[0]
        lon, lat = lat_lon.split(",")

        names = sel.xpath('//div[@class="fl l-txt"]/a/text()').extract()
        district = names[2][:-2]
        area = names[3][:-2]

        s = [district, area, name, price, lon, lat]
        # # self.f.write("\n")
        # # ss = ",".join(s).encode("utf-8")
        self.writer.writerow(s)
        print(s)
        # with open("C:\\Users\\Administrator\\Desktop\\lbs\\house_price.csv", 'w') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow([district, area, name, price, lat_lon])

    def closed(self):
        self.writer.close()
