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
unique_urls = set()

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

# English stopwords
stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren\'t", "as", "at",
            "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
            "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
            "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
            "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
            "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
            "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
            "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
            "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
            "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
            "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
            "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
            "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]
subdomainInfo = SubdomainInfo()

# initialize scraper
#   blacklist pattern list
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


def print_info():
    print(Counter(token_list).most_common(50))
    print("Number of unique urls:" + len(unique_urls))
    print("longest page:" + longest_page)

# saves blacklist pattern list to file path provided
def save_blacklist(blacklistsavepath):
    with open(blacklistsavepath, "w") as f:
        f.write("\n".join(blacklist.keys()))

# Check if there is any repetition in path in the URL, if there is then do not add it to the frontier
def getPathRepeat(urlpath):
    lst = urlpath.split('/')
    dict1 = dict(Counter(lst))
    return [key for key,value in dict1.items() if value > config.path_repeat_threshold]

token_list = []
longest_page = ""
longest_cnt = 0
# Tokenize a string into a list of words and put into token list, also finding the longest page
def tokenizer(string, url):
    global longest_page
    global longest_cnt
    string = string.lower()
    lst = re.split(r'[\s]+', string)
    for word in stopwords:
        if word in lst:
            lst.remove(word)

    # Compare this page's content with the longest page
    if len(lst) >= longest_cnt:
        longest_page = url
        longest_cnt = len(lst)
    token_list.extend(lst)
    return None

def allurlchecks(url):
    return is_valid(url) and not is_blacklisted(url) and not is_trap(url)

def response_invalid(resp):
    return resp.status != 200 or not resp.raw_response or not resp.raw_response.content or not is_valid(resp.url)

def scraper(url, resp):
    links = sort_by_query(extract_next_links(url, resp))
    return [link for link in links if allurlchecks(link) and subdomainInfo.process_url(link).canFetch(link)]

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

    # Extract text from the page
    text = ' '.join(e.text_content() for e in tree.xpath('//*[self::title or self::p or self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6 or self::a]'))

    # Tokenize the text and add to token list
    tokenizer(text,url)

    extracted = set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href|.//loc/text()')])
    
    #Add this url to unique urls
    unique_urls.add(url)

    return extracted
    

# sort_by_query will sort querys
# remove any urls with same query parameters
# pointless to run if majority of links have no query parameters
def sort_by_query(links):
    sorted_links = set() # Return 

    for url in links:
        parsed = urlparse(url)
        # extract/sort query 
        query = parsed.query.split("&")
        query.sort()

        query_string = "&".join(query)
        
        # url with sorted query
        new_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query_string, parsed.fragment))

        #adding to set removes duplicates
        sorted_links.add(new_url)
    
    return list(sorted_links)

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
