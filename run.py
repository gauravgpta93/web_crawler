import sys
import time

from config.constants import WEB_SIZE, WEB_DEGREE
from crawler import WebCrawler
from web import Web

if __name__ == '__main__':
    if len(sys.argv) == 3:
        WEB_SIZE = int(sys.argv[1])
        WEB_DEGREE = int(sys.argv[2])
    web = Web(size=WEB_SIZE, degree=WEB_DEGREE)
    crawler = WebCrawler()
    start = time.time()
    urls = crawler.crawl(web)
    finish = time.time()
    print("Time took to crawl the URLs: ", finish - start)
    print("Number of URLs found: ", len(urls))
    assert len(urls) == WEB_SIZE
