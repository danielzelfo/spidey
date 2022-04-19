import re
from urllib.parse import urlparse, urljoin, urldefrag, urlunsplit
from lxml import html
from collections import Counter
import os
from utils.download import download
import time
import robotparser

blacklist = {}
temp_blacklist = {}

config = None
frontier = None

class SubdomainInfo:
    class SubdomainEntry:
        def __init__(self, netloc):
            self.netloc = netloc
            self.robots = None
        
        def canFetch(self, url):
            return self.robots is None or self.robots.can_fetch('*', url)

        def process_robots(self, url):
            robotsurl = url.split(self.netloc)[0] + self.netloc+"/robots.txt"

            resp = download(robotsurl, config)
            time.sleep(config.time_delay)

            if response_invalid(resp):
                return

            ab_path = os.path.join(os.getcwd(), config.robots_file)
            with open(ab_path, "wb") as f:
                f.write(resp.raw_response.content)
            
            self.robots = robotparser.RobotFileParser()
            self.robots.set_url("file://"+ab_path)
            self.robots.read()            
            os.unlink(ab_path)

            for sitemapurl in self.robots.site_maps():
                print("ADDED SITEMAP:", sitemapurl)

                if sitemapurl.lower().endswith(".txt"):
                    resp = download(sitemapurl, config)
                    time.sleep(config.time_delay)
                    if not response_invalid(resp):
                        for fromsitemaptxt in resp.raw_response.content.splitlines():
                            frontier.add_url(fromsitemaptxt)
                            print("FRONTIER ADDED:", fromsitemaptxt)
                elif allurlchecks(sitemapurl):
                    frontier.add_url(sitemapurl)
                    print("FRONTIER ADDED:", sitemapurl)


    def __init__(self):
        self.data = {}
    
    def process_url(self, url):
        netloc = urlparse(url).netloc
        if not netloc in self.data:
            print("NEWSUBDOMAIN:", netloc)
            subdomainEntry = self.SubdomainEntry(netloc)
            subdomainEntry.process_robots(url)
            self.data[netloc] = subdomainEntry
            return subdomainEntry
        
        return self.data[netloc]

scheme_pattern = re.compile(r"^https?$")
netloc_pattern = re.compile(r"^(([-a-z0-9]+\.)*(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu))"
                            +r"|today\.uci\.edu\/department\/information_computer_sciences$")
# Extensions not being crawled
bad_ext_path_pattern = re.compile(r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")

subdomainInfo = SubdomainInfo()

# initialize scraper
#  blacklist pattern list
#   
def init(tconfig, tfrontier):
    global config, frontier
    config = tconfig
    frontier = tfrontier

    if os.path.exists(config.blacklist_file):
        with open(config.blacklist_file, "r") as f:
            for pattern in f.readlines():
                pattern = pattern.strip()
                blacklist[pattern] = re.compile(pattern)

# saves blacklist pattern list to file path provided
def save_blacklist(blacklistsavepath):
    with open(blacklistsavepath, "w") as f:
        f.write("\n".join(blacklist.keys()))

# Check if there is any repetition in path in the URL, if there is then do not add it to the frontier
def getPathRepeat(urlpath):
    lst = urlpath.split('/')
    dict1 = dict(Counter(lst))
    return [key for key,value in dict1.items() if value > config.path_repeat_threshold]
def allurlchecks(url):
    return is_valid(url) and not is_blacklisted(url) and not is_trap(url)

def response_invalid(resp):
    return resp.status != 200 or not resp.raw_response or not resp.raw_response.content or not is_valid(resp.url)
  

def scraper(url, resp, frontier):
    links = extract_next_links(url, resp, frontier)
    return list(set(sort_by_query(link) for link in links if allurlchecks(link) and subdomainInfo.process_url(link).canFetch(link)))


def absolute_url(page_url, outlink_url):
    # join urls | note: if outlink_url is an absolute url, that url is used
    newurl = urljoin(page_url, outlink_url)
    # remove fragment
    return urldefrag(newurl)[0]

def extract_next_links(url, resp):
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if response_invalid(resp):
        return set()
    
    # check if redirect is blacklisted
    if resp.url != url and is_blacklisted(resp.url):
        return set()
    
    # check if redirect is a trap
    if resp.url != url and is_trap(resp.url):
        return set()
    
    try:
        tree = html.fromstring(resp.raw_response.content) #check if urls are valid
    except:
        return set()


    return set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href|.//loc/text()')])


    
# sort_by_query will sort a link by querys
# returns a single url with a sorted query
def sort_by_query(link):
    parsed = urlparse(link)
    # extract query 
    query = parsed.query.split("&")
    #only sort if query has more than 2 or more parameters
    if(len(query) >= 2):
        #sort query 
        query.sort()
        #build new query with sorted parameters
        query_string = "&".join(query)
        #new url with sorted query
        new_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query_string, parsed.fragment)) 
        return new_url
    else:
        return link
   

# check if a url is blacklisted
#   uses the permanent and temporary blacklists
def is_blacklisted(url):
    for pattern in blacklist:
        if blacklist[pattern].match(url):
            return True
    for pattern in temp_blacklist:
        if temp_blacklist[pattern].match(url):
            return True
    return False

# check if a url is a trap
#   checks repeating url pattern
#       all sibling directories of the first directory in the url path that repeats and their children are PERMANENTLY blacklisted
#           EX: https://www.example.com/x/a/b/c/a/b/c/a/b/c
#               => permanent blacklist https://www.example.com/x.*
#               if another pattern is included in the new blacklist pattern, it will be removed.
#                    EX: https://www.example.com/x/y.* would be removed since it is included in https://www.example.com/x.*
#       if a directory repeats a set number of times in the path, it will be a key that is temporarily blacklisted from the crawling of the domain
#       this is done to speed up the process of finding the highest level directory that is causing an endless path repetition loop
#           EX: https://www.example.com/x/a/b/c/a/b/c/a/b/c
#               => temporarily blacklist https://www.example.com/.*a, https://www.example.com/x/.*b, https://www.example.com/x/a/.*c
def is_trap(url):
    parsed = urlparse(url)
    urlpath = parsed.path.lower()
    repeats = getPathRepeat(urlpath)
    if len(repeats) != 0:
        urlpart = url[:min(url.find(repeat) for repeat in repeats)-1]
        patternstr = f"{re.escape(urlpart)}.*"
        regex = re.compile(patternstr)
        todel = []
        for pattern in blacklist:
            if pattern.startswith(patternstr[:-2]):
                todel.append(pattern)
        for p in todel:
            del blacklist[p]
        blacklist[patternstr] = regex
        frontier.cancel_urls(regex)

        for r in repeats:
            pattern = f"{re.escape('/'.join(urlpart.split('/')[:-1]))}\\/.*{r}"
            tempregex = re.compile(pattern)
            temp_blacklist[pattern] = tempregex
            frontier.cancel_urls(tempregex) 
           
        return True
    return False

# check if the scheme, netloc, and path of the url are valid
def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        return (scheme_pattern.match(parsed.scheme.lower()) 
                and netloc_pattern.match(parsed.netloc.lower()) 
                and not bad_ext_path_pattern.match(parsed.path.lower()))
    except TypeError:
        print ("TypeError for ", parsed)
        raise
