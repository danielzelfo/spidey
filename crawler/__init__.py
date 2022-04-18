from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
import scraper

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        scraper.init(self.config, self.frontier)

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()
        scraper.save_blacklist(self.config.blacklist_file)

    def join(self):
        for worker in self.workers:
            worker.join()
