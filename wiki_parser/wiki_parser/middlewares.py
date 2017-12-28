# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import Request
import tldextract
from scrapy import log


class WikiParserSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DomainDepthMiddleware(object):
    def __init__(self, domain_depths, default_depth):
        self.domain_depths = domain_depths
        self.default_depth = default_depth

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        domain_depths = settings.getdict('DOMAIN_DEPTHS', default={})
        default_depth = settings.getint('DEPTH_LIMIT', 1)

        return cls(domain_depths, default_depth)

    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                # get max depth per domain
                domain = tldextract.extract(request.url).registered_domain
                maxdepth = self.domain_depths.get(domain, self.default_depth)

                depth = response.meta.get('depth', 0) + 1
                request.meta['depth'] = depth

                if maxdepth and depth > maxdepth:
                    log.msg(format="Ignoring link (depth > %(maxdepth)d): %(requrl)s ",
                            level=log.DEBUG, spider=spider,
                            maxdepth=maxdepth, requrl=request.url)
                    return False
            return True

        return (r for r in result or () if _filter(r))