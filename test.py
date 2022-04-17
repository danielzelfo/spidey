import os
import re
from collections import Counter
import requests
from utils.download import download
from configparser import ConfigParser
from utils.config import Config
from utils.server_registration import get_cache_server
import robotparser

cparser = ConfigParser()
cparser.read("config.ini")
config = Config(cparser)
config.cache_server = get_cache_server(config, False)

resp = download("https://gitlab.ics.uci.edu/robots.txt", config)

ab_path = os.path.join(os.getcwd(), "TEMP_ROBOTS.txt")
# urllib.request.urlopen("file://"+ab_path)
# with open(ab_path, "wb") as f:
#     f.write(resp.raw_response.content)


rp = robotparser.RobotFileParser()
rp.set_url("file://"+ab_path)
rp.read()
rrate = rp.request_rate("")
rp.crawl_delay("")

print(rp.can_fetch('*', "https://gitlab.ics.uci.edu/users/apowjopajwfa/aopjwapojfwa/snippets"))