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

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['caption', 'logo', 'website_link', 'table_data', 'content']
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, priority=1)

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
                item['url'] = link.url
                if item.get('url') not in items:
                    items.append(item.get('url'))

        for i in items:
            try:
                yield scrapy.Request(i, callback=self.parse_data)  # Extracting media information
            except ValueError:
                pass

    def parse_data(self, response):
        tds = []
        ths = []
        total = []

        for i in response.xpath('//table[@class="infobox vcard"]'):
            items = TableParserItem()
            try:
                items['logo'] = i.xpath('.//td[@class="logo"]/a/@href').extract()[0]
            except IndexError:
                pass

            try:
                items['caption'] = i.xpath('//caption[@class="fn org"]//text()').extract()[0]
                items['table_data'] = {}
                c = i.xpath('//*[@id="mw-content-text"]/div/p[1]//text()').extract()
                cont = [w.strip() for w in c if w.replace('\n', '')]
                items['content'] = cont
                items['website_link'] = i.xpath('.//a[@class="external text"]/@href').extract()[0]
            except IndexError:
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

            total = zip(ths, tds)
            try:
                for k, v in total:
                    items['table_data'][k] = v
            except:
                pass

            data = items.get('table_data', None)

            type_data = False
            industry_data = False

            if data:
                industry = data.get('Industry', None)
                mt = data.get('Type', None)
                content = items.get('content', None)

                if mt:
                    mt = mt.lower().split(' ')
                    for ii in mt:
                        if any(media_item in ii for media_item in self.media_types):
                            print('!!!! TYPE !!!!')
                            print(items.get('caption', None))
                            print(mt)
                            type_data = True
                            yield items
                            break

                    if not type_data:
                        if industry:
                            industry = industry.lower().split(' ')
                            for ii in industry:
                                if any(media_item in ii for media_item in self.media_types):
                                    print('!!!! INDUSTRY !!!!')
                                    print(items.get('caption', None))
                                    print(industry)
                                    industry_data = True
                                    yield items
                                    break

                        if not industry_data:
                            if content:
                                for ii in content:
                                    if any(media_item in ii for media_item in self.media_types):
                                        print('!!!! CONTENT !!!')
                                        print(items.get('caption', None))
                                        print(content)
                                        yield items
                                        break

                elif not mt:
                    if not type_data:
                        if industry:
                            industry = industry.lower().split(' ')
                            for ii in industry:
                                if any(media_item in ii for media_item in self.media_types):
                                    print('!!!! INDUSTRY !!!!')
                                    print(items.get('caption', None))
                                    print(industry)
                                    industry_data = True
                                    yield items
                                    break

                        if not industry_data:
                            if content:
                                for ii in content:
                                    if any(media_item in ii for media_item in self.media_types):
                                        print('!!!! CONTENT !!!')
                                        print(items.get('caption', None))
                                        print(content)
                                        yield items
                                        break