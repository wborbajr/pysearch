from googlesearch import search

import logging
logger = logging.getLogger(__name__)


class SearchBot:

    def __init__(self):

        __version__ = '0.1.0'
        __name__ = 'SearchBot'

        logger.info(" {0}: {1} ".format(__name__, __version__))

        # self.content = content

    def googleSearch(self, content):
        return search(content, stop=20)
