# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class WikiParserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()


class TableParserItem(scrapy.Item):
    caption = scrapy.Field()
    logo = scrapy.Field()
    table_data = scrapy.Field()