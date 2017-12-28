Requrements:

requirements.txt

Installation:

virtualenv -p python3 <env>

cd <env>

source bin/activate

pip intall -r requirements.txt

git clone https://github.com/alexstone23/wiki_parser.git

cd wiki_parser/wiki_parser/

scrapy crawl wiki -o agency.csv -t csv

For recursive crawling use linker spider

1) Navigate into <env>/lib/python3.5/site-packages/scrapy/settings/default_settings.py

2) Set up SPIDER MIDDLEWARES

SPIDER_MIDDLEWARES = {
    'wiki_parser.middlewares.DomainDepthMiddleware': 900,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': None
}


3) Set DEPTH_LIMIT in settings.py

4) scrapy crawl linker -o media_data.csv -t csv --loglevel=INFO




