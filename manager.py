import logging
import logging.config


from search import SearchBot
from process import ProcessBot


def logsetup():
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    return logging.getLogger(__name__)


def main():
    logger = logsetup()
    logger.info('Started')

    result = SearchBot().googleSearch('"lotofacil resultado" 1757')
    ProcessBot().processSearch(result)

    logger.info('Finished')


if __name__ == '__main__':
    main()
