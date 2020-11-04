# Hint:
#   1. While your solution must handle the case for Web(size=123, degree=5) in
#      the test script, you may want to use different size and degree settings
#      for faster tests and for better test coverage.

import time

from crawler import WebCrawler
from web import Web

size = 1000
degree = 10
web = Web(size=size, degree=degree)
crawler = WebCrawler()
start = time.time()
urls = crawler.crawl(web)
finish = time.time()
print("Time took to crawl the URLs: ", finish - start)
print("Number of URLs found: ", len(urls))
assert len(urls) == size
