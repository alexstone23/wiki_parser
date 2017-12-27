# -*- coding: utf-8 -*-
import scrapy
from wiki_parser.items import WikiParserItem, TableParserItem
from scrapy.spiders import CrawlSpider


class WikiSpider(CrawlSpider):
    name = 'wiki'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/News_agency']

    # Exclude images, styles, scripts etc.
    restricted_ext = ['ico', 'js', 'rss', 'css', 'png']

    def links_extractor(self, response):
        arr = []
        for sel in response.xpath('//*[@href]'):
            item = WikiParserItem()
            item['url'] = sel.xpath('@href').extract()

            for i in item['url']:
                ext = i.split('.')  # Check extension validness
                if ext[-1] not in self.restricted_ext:
                    arr.append(i)
        return arr

    def parse(self, response):
        arr = self.links_extractor(response)  # Extracting links from start url page

        for u in arr:
            try:
                yield scrapy.Request(response.urljoin(u), callback=self.parse_data)  # Extracting media information
            except ValueError:
                pass

    def parse_data(self, response):

        tds = []
        ths = []
        total = []

        # Processing media info card
        for i in response.xpath('//table[@class="infobox vcard"]'):
            items = TableParserItem()
            try:
                items['caption'] = i.xpath('//caption[@class="fn org"]//text()').extract()[0]
                items['logo'] = i.xpath('.//td[@class="logo"]/a/@href').extract()[0]
                items['table_data'] = {}
            except:
                pass

            # If media hasn't at least a name - skipping
            if not items.get('caption', None):
                break

            # Extracting cell text
            for t in i.xpath('.//tr/td'):
                td = t.xpath('.//text()').extract()
                td = [t.replace('\n', '').replace('\xa0', ' ') for t in td]

                if td:
                    tds.append(''.join(td))

            # Extracting th text
            for h in i.xpath('.//tr/th'):
                th = h.xpath('.//text()').extract()
                th = [t for t in th if t.replace('\n', '').replace('\xa0', ' ')][0]
                ths.append(th)

            # Merging lists
            total = zip(ths, tds)
            try:
                for k, v in total:
                    # Writing data into dict
                    items['table_data'][k] = v
            except KeyError:
                pass

            yield items