# -*- coding: utf-8 -*-
import scrapy
from wiki_parser.items import TableParserItem


class TableparseSpider(scrapy.Spider):
    name = 'tableparse'
    allowed_domains = ['https://en.wikipedia.org/']
    start_urls = ['https://en.wikipedia.org/wiki/Catalan_News_Agency']

    def parse(self, response):
        tds = []
        ths = []
        total = []

        for i in response.xpath('//table[@class="infobox vcard"]'):
            items = TableParserItem()
            items['caption'] = i.xpath('//caption[@class="fn org"]/text()').extract()[0]
            items['logo'] = i.xpath('.//td[@class="logo"]/a/@href').extract()[0]
            items['table_data'] = {}

            for t in i.xpath('.//tr/td'):
                td = t.xpath('.//text()').extract()
                td = [t.replace('\n', '').replace('\xa0', ' ') for t in td]

                if td:
                    tds.append(''.join(td))

            for h in i.xpath('.//tr/th'):
                th = h.xpath('.//text()').extract()
                th = [t for t in th if t.replace('\n', '')][0]
                ths.append(th)

            total = zip(ths, tds)
            for k, v in total:
                items['table_data'][k] = v

            #print(items['table_data']['Industry'])

            yield items

