import re
from urllib.parse import urlparse, urljoin, urldefrag
from lxml import html
from collections import Counter
import os

### FOR TESTING
TEMPORARYREGEX = re.compile(r"^\/ugrad\/honors\/index\.php\/")
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

# DEFAULTS - these are replace by the config.ini file
#   threshold for a repeating directory in the url path 
path_repeat_threshold = 3
#   path to save permanent blacklist
blacklistfilepath = "blacklist_save.txt"

blacklist = {}
temp_blacklist = {}

# initialize scraper
#   blacklist pattern list
#   
def init(config):
    global blacklistfilepath, path_repeat_threshold
    blacklistfilepath = config.blacklist_file
    path_repeat_threshold = config.path_repeat_threshold

    if os.path.exists(blacklistfilepath):
        with open(blacklistfilepath, "r") as f:
            for pattern in f.readlines():
                blacklist[pattern] = re.compile(pattern)

# saves blacklist pattern list to file path provided
def save_blacklist(blacklistsavepath):
    with open(blacklistsavepath, "w") as f:
        f.write("\n".join(blacklist.keys()))

# Check if there is any repetition in path in the URL, if there is then do not add it to the frontier
def getPathRepeat(urlpath):
    lst = urlpath.split('/')
    dict1 = dict(Counter(lst))
    return [key for key,value in dict1.items() if value > path_repeat_threshold]

def scraper(url, resp, frontier):
    links = extract_next_links(url, resp, frontier)
    return [link for link in links if is_valid(link) and not is_blacklisted(link) and not is_trap(link, frontier)]

def absolute_url(page_url, outlink_url):
    # join urls | note: if outlink_url is an absolute url, that url is used
    newurl = urljoin(page_url, outlink_url)
    # remove fragment
    return urldefrag(newurl)[0]

def extract_next_links(url, resp, frontier):
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content or not is_valid(resp.url):
        return set()
    
    # check if redirect is blacklisted
    if resp.url != url and is_blacklisted(resp.url):
        return set()
    
    # check if redirect is a trap
    if resp.url != url and is_trap(resp.url, frontier):
        return set()
    
    try:
        tree = html.fromstring(resp.raw_response.content)
    except:
        return set()
    
    outlink = set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href')])
    
    return outlink

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
#               => temporarily blacklist https://www.example.com/.*a, https://www.example.com/.*b, https://www.example.com/.*c
def is_trap(url, frontier):
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
        urlpath = parsed.path.lower()
        return scheme_pattern.match(parsed.scheme.lower()) and netloc_pattern.match(parsed.netloc.lower()) and TEMPORARYREGEX.match(urlpath) and not bad_ext_path_pattern.match(urlpath)
    except TypeError:
        print ("TypeError for ", parsed)
        raise
