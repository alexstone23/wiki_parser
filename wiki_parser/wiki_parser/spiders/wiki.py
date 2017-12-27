# -*- coding: utf-8 -*-
import scrapy
from wiki_parser.items import WikiParserItem, TableParserItem

from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule


class WikiSpider(scrapy.Spider):
    name = 'wiki'
    allowed_domains = ['https://en.wikipedia.org/']
    start_urls = ['https://en.wikipedia.org/wiki/News_agency']
    '''
    rules = (Rule(LinkExtractor(), callback='parse_url', follow=True), )
    '''
    '''
    def parse_url(self, response):
        item = WikiParserItem()
        item['url'] = response.url
        yield item
        #print(url)
    '''
    '''
        try:
            yield scrapy.Request(url, callback=self.parse_data)
        except ValueError:
            print('Err')
            pass
    '''
    def link_checker(self, url):
        input_url = url.split('/')
        if input_url[0] != 'https:':
            if input_url[0] != 'http:':
                domain = ''.join(self.allowed_domains)
                mod_url = "%s%s" % (domain, url.strip('\\').strip('/'))
                return mod_url
            else:
                return url
        else:
            return url

    def parse(self, response):
        arr = []
        for sel in response.xpath('//*[@href]'):
            item = WikiParserItem()
            item['url'] = sel.xpath('@href').extract()
            #print(item['url'])

            for i in item['url']:
                arr.append(self.link_checker(i))
        #print(arr)
        for u in arr:
            try:
                yield scrapy.Request(u, callback=self.parse_data)
            except ValueError:
                print('Err')
                pass

    def parse_data(self, response):
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
            #print(items)

            yield items
