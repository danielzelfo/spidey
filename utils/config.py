import re


class Config(object):
    def __init__(self, config):
        self.user_agent = config["IDENTIFICATION"]["USERAGENT"].strip()
        print (self.user_agent)
        assert self.user_agent != "DEFAULT AGENT", "Set useragent in config.ini"
        assert re.match(r"^[a-zA-Z0-9_ ,]+$", self.user_agent), "User agent should not have any special characters outside '_', ',' and 'space'"
        self.threads_count = int(config["LOCAL PROPERTIES"]["THREADCOUNT"])
        self.save_file = config["LOCAL PROPERTIES"]["SAVE"]
        self.blacklist_file = config["LOCAL PROPERTIES"]["BLACKLIST"]
        self.temp_scraper_info = config["LOCAL PROPERTIES"]["TEMP_SCRAPER_INFO"]
        self.temp_scraper_subdomain_info = config["LOCAL PROPERTIES"]["TEMP_SCRAPER_SUBDOMAIN_INFO"]
        self.robots_file = config["LOCAL PROPERTIES"]["LOCAL_ROBOTS"]

        self.host = config["CONNECTION"]["HOST"]
        self.port = int(config["CONNECTION"]["PORT"])

        self.seed_urls = config["CRAWLER"]["SEEDURL"].split(",")
        self.time_delay = float(config["CRAWLER"]["POLITENESS"])
        self.path_repeat_threshold = float(config["CRAWLER"]["PATH_REPEAT_THRESHOLD"])

        self.cache_server = None