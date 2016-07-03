import logging

logger = logging.getLogger(__name__)

class Crawler(object):
    def __init__(self, source, processors):
        self._source = source

        if isinstance(processors, list):
            self._processors = processors
        else:
            self._processors = [processors] 

    def run(self):
        logger.info("Starting the crawler")

        generator = self._source.items()

        while True:
            try:
                item_data = generator.next()
            except StopIteration:
                return
            except:
                logger.exception("failed to fetch items")
                raise

            for processor in self._processors:
                processor.process_item(item_data)
