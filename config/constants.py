# Number of retires on get(url) before we give up on that url
RETRY_COUNT = 5

# Total threads available for
TOTAL_THREADS = 20

# Time a queue can be empty before the thread exits
QUEUE_TIMEOUT = 5

# Parameters for web() object
WEB_SIZE = 1000
WEB_DEGREE = 10

# This is to define the logging level that we want in our logging file
# 5: logging.DEBUG [Most LOGS]
# 4: logging.INFO
# 3: logging.WARNING
# 2: logging.ERROR
# 1: logging.CRITICAL [Least LOGS]
LOGGING_LEVEL = 4
LOGGING_FILE_NAME = "Crawler log"
