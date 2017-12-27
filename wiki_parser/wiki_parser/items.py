# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiParserItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class TableParserItem(scrapy.Item):
    caption = scrapy.Field()
    logo = scrapy.Field()
    table_data = scrapy.Field()