import ast
import threading
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from time import perf_counter

import backoff

from Helper.logger import Logger
from config.constants import RETRY_COUNT, TOTAL_THREADS, QUEUE_TIMEOUT
from web import Web


class WebCrawler:
    def __init__(self):
        self._lock = threading.Lock()
        self._total_threads = TOTAL_THREADS
        self._parsed_urls = set()
        self._to_parse = Queue()
        self._to_parse_set = set()
        self._web_object = None
        self._failed_url_list = list()

        # Logger initialization
        logger = Logger()
        self._logger = logger.get_logger()

    # use the timer decorator if we want to time the function runtime. Uncomment the below to check runtime of crawl.
    # @timer
    def crawl(self, web_object):
        """
        This function is called the web crawler which goes calls the root url and gets all the linked pages to the root.
        :param web_object: The web simulator object with 2 functions, root() and get()
        :return: List of URLS which are linked directly or indirectly to the root of web_object
        """
        self._logger.info("Started the web crawl")
        start_time = perf_counter()
        self._web_object = web_object
        root = web_object.root()
        if root not in self._parsed_urls:
            # In case the same crawler object is called multiple times, we avoid doing multiple gets on the root url
            self._to_parse.put(root)

        # In case we want to use ThreadPool implementation for using multiple threads.
        self._thread_pool_crawl()

        # We use the below if we want to manually create and start the threads.
        # self._manual_thread_crawl()

        end_time = perf_counter()
        self._logger.info("Total passed URL's: %s" % len(self._parsed_urls))
        self._logger.info("Total time taken to run web crawl: %s" % str(end_time - start_time))
        return list(self._parsed_urls)

    def get_failed_urls(self):
        """
        This function returns the list of urls that failed the web_object.get() more than the allocated retires count.
        :return: list of failed URL
        """
        return self._failed_url_list

    def _thread_pool_crawl(self):
        """
        This is a function which uses ThreadPool from concurrent library to create a thread pool and assign the function
        to crawl the urls.
        :return:
        """
        self._logger.debug("Starting to create thread pool of %s workers" % str(self._total_threads))
        thread_pool = ThreadPoolExecutor(max_workers=self._total_threads)
        threads = list()
        for _ in range(self._total_threads):
            threads.append(thread_pool.submit(self._web_crawl))
        futures.wait(threads)

    def _manual_thread_crawl(self):
        """
        This function creates and starts the threads manually. I have added this function as a additional way to
        multi thread although the performance is identical to the ThreadPool.
        :return:
        """
        workers = []
        for i in range(self._total_threads):
            worker = threading.Thread(target=self._web_crawl)
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()

    def _web_crawl(self):
        """
        This function does a get on the url and saves the new urls to be parsed later.
        In case the get fails, we add that to another list to be parsed later. This is a BFS approach
        :return:
        """
        try:
            while True:
                # Get a URL from the queue. If queue is empty for 5 seconds we get a Empty Exception, and then we close
                # the thread. If the get function is too slow, we can increase the timeout.
                url = self._to_parse.get(timeout=QUEUE_TIMEOUT)
                if url not in self._parsed_urls:
                    try:
                        crawled_urls = self._url_get(url)

                        crawled_urls = ast.literal_eval(crawled_urls)
                        with self._lock:
                            # We add a lock to make adding to set thread safe.
                            self._parsed_urls.add(url)

                        # check not already added parsed_url
                        crawled_urls = [x for x in crawled_urls if x not in self._parsed_urls]
                        # check not already added to_parse_set
                        crawled_urls = [x for x in crawled_urls if x not in self._to_parse_set]

                        with self._lock:
                            # We add a lock to make adding to set thread safe.
                            self._to_parse_set.update(crawled_urls)
                        for url in crawled_urls:
                            # Since Queue is thread safe we can add without lock.
                            self._to_parse.put(url)
                    except Exception:
                        with self._lock:
                            # Exception is raised if we are not able to get within the retires count that we specified.
                            # We add a lock to make adding to list thread safe.
                            self._logger.debug("Failed for URL after retries: %s" % url)
                            self._failed_url_list.append(url)

        except Empty:
            return

    # We added a exponential backoff in case of failed URL, this is useful as we have a multi thread implementation and
    # we want to increase the robustness of our code. Also Exponential backoff is standard practise in scenarios of
    # retries, specially for applications like api get calls.
    @backoff.on_exception(backoff.expo, Exception, max_tries=RETRY_COUNT)
    def _url_get(self, url):
        """
        This calls the web_object.get() and checks if an error is raised. In case of an error, We retry with exponential
        backoff until we have the proper get() response or we exceed the number of retires.
        The reason we implement a separate function for this is because we want to increase the robustness of our
        crawler, since we cannot control the web_object.get() command.

        :param url: URL on which we do a web_object.get()
        :return: list(list_of_linked_url) or raises exception if we have fail for more than the allocated retries.
        """
        try:

            # We use the below if we are SURE that the web_object.get() is not a blocking call. For the purposes of this
            # use case, this is sufficient.
            crawled_url = self._web_object.get(url)
            self._logger.debug("Successful GET on URL: %s" % str(url))
            return crawled_url

        except Exception as e:
            # We raise the exception if web_object.get() fails. We can improve the Type of Exceptions as and when they
            # happen. For now I have gone with a general broad Exception class.
            self._logger.error("Unable to do a GET on URL: %s. Error: %s" % (url, str(e)))
            raise Exception


if __name__ == '__main__':
    web = Web(size=100, degree=1)
    crawler = WebCrawler()
    urls = crawler.crawl(web)
    # urls1 = crawler.crawl(web)
    print(urls)
    print(len(urls))
