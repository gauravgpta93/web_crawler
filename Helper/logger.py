import logging
import os

from config.constants import LOGGING_LEVEL, LOGGING_FILE_NAME

LOGGING_LEVEL_DICT = {
    5: logging.DEBUG,
    4: logging.INFO,
    3: logging.WARNING,
    2: logging.ERROR,
    1: logging.CRITICAL,
}


class Logger:
    def __init__(self):
        """
        Initialize the logger
        """
        # file_name = os.path.join("./log_file", LOGGING_FILE_NAME)
        logging_level = LOGGING_LEVEL_DICT[LOGGING_LEVEL]
        logging.basicConfig(filename=LOGGING_FILE_NAME, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                            level=logging_level)
        self.logger = logging.getLogger('Web_Crawler_logger')

    def get_logger(self):
        """
        Get the logger object
        :return: logger object
        """
        return self.logger
