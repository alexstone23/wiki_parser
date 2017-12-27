# -*- coding: utf-8 -*-
import scrapy


class LinkerSpider(scrapy.Spider):
    name = 'linker'
    allowed_domains = ['https://en.wikipedia.org/wiki/News_agency']
    start_urls = ['http://https://en.wikipedia.org/wiki/News_agency/']

    def parse(self, response):
        pass
