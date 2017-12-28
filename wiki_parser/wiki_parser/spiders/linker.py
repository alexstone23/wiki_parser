# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from wiki_parser.items import WikiParserItem, TableParserItem


class LinkerSpider(CrawlSpider):
    name = 'linker'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/News_agency']
    restricted_ext = ['ico', 'js', 'rss', 'css', 'png']
    extracted_links = []
    media_types = ['news media', 'news agency', 'radio', 'television', 'media analytics', 'newspapers', 'press agency', 'telecomunications']
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_items"
        )
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse_items(self, response):
        items = []
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        for link in links:
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True

            if is_allowed:
                item = WikiParserItem()
                item['name'] = response.url
                item['url'] = link.url
                items.append(item)

        for i in items:
            try:
                yield scrapy.Request(i.get('url', None), callback=self.parse_data)  # Extracting media information
            except ValueError:
                pass

    def parse_data(self, response):
        tds = []
        ths = []
        total = []

        for i in response.xpath('//table[@class="infobox vcard"]'):
            items = TableParserItem()
            try:
                items['caption'] = i.xpath('//caption[@class="fn org"]//text()').extract()[0]
                items['logo'] = i.xpath('.//td[@class="logo"]/a/@href').extract()[0]
                items['table_data'] = {}
            except:
                pass

            if not items.get('caption', None):
                break

            for t in i.xpath('.//tr/td'):
                td = t.xpath('.//text()').extract()
                try:
                    td = [t.replace('\n', '').replace('\xa0', ' ') for t in td]
                except:
                    pass

                if td:
                    tds.append(''.join(td))

            for h in i.xpath('.//tr/th'):
                th = h.xpath('.//text()').extract()
                try:
                    th = [t for t in th if t.replace('\n', '').replace('\xa0', ' ')][0]
                except:
                    pass
                ths.append(th)

            try:
                c = [w.strip() for w in c if w.replace('\n', '')]
            except:
                pass

            items['content'] = c

            total = zip(ths, tds)
            try:
                for k, v in total:
                    items['table_data'][k] = v
            except KeyError:
                pass

            data = items.get('table_data', None)
            content = items.get('content', None)

            if data:
                industry = data.get('Industry', None)
                mt = data.get('Type', None)

                if mt:
                    mt = mt.lower().split(' ')
                    for ii in mt:
                        if any(ii in media_item for media_item in self.media_types):
                            print('!!!! TYPE !!!!')
                            print(data)
                            yield items
                            break

                if industry:
                    industry = industry.lower().split(' ')
                    for ii in industry:
                        if any(ii in media_item for media_item in self.media_types):
                            print('!!!! INDUSTRY !!!!')
                            print(data)
                            yield items
                            break

            if content:
                for ii in content:
                    if any(ii in media_item for media_item in self.media_types):
                        print('!!!! CONTENT !!!')
                        print(data)
                        yield items
                        break