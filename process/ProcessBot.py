import logging
logger = logging.getLogger(__name__)


class ProcessBot:

    # def __init__(self, content):
    @property
    def __init__(self):

        __version__ = '0.1.0'
        __name__ = 'ProcessBot'

        logger.info(" {0}: {1} ".format(__name__, __version__))

        # self.content = content

    @property
    def processSearch(self, content):
        for result in content:
            print(result)
