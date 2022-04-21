import re
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin, urldefrag, urlunsplit
from lxml import html
from lxml import etree
from collections import Counter
import os
from utils.download import download
import time
import robotparser
from bs4 import BeautifulSoup as BS
from bs4.element import Comment


blacklist = {}
temp_blacklist = {}
unique_urls = set()
query_dict = {}

token_list = []
longest_page = ""
longest_cnt = 0

config = None
frontier = None

class SubdomainInfo:
    class SubdomainEntry:
        def __init__(self, netloc):
            self.netloc = netloc
            self.robots = None
            self.num_urls = 0
        
        def canFetch(self, url):
            return self.robots is None or self.robots.can_fetch('*', url)

        def process_robots(self, url):
            robotsurl = url.split(self.netloc)[0] + self.netloc+"/robots.txt"

            resp = download(robotsurl, config)
            time.sleep(config.time_delay)

            if response_invalid(resp) or not is_valid(resp.url):
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
                    if not (response_invalid(resp) or not is_valid(resp.url)):
                        for fromsitemaptxt in resp.raw_response.content.splitlines():
                            frontier.add_url(fromsitemaptxt)
                            print("FRONTIER ADDED:", fromsitemaptxt)
                elif allurlchecks(sitemapurl):
                    frontier.add_url(sitemapurl)
                    print("FRONTIER ADDED:", sitemapurl)


    def __init__(self):
        self.data = {}
        self.icssubdomains = []
    
    def process_url(self, url):
        netloc = urlparse(url).netloc
        if not netloc in self.data:
            print("NEWSUBDOMAIN:", netloc)
            subdomainEntry = self.SubdomainEntry(netloc)
            subdomainEntry.process_robots(url)
            self.data[netloc] = subdomainEntry

            if netloc == "ics.uci.edu" or netloc.endswith(".ics.uci.edu"):
                self.icssubdomains.append(netloc)

            return subdomainEntry
        
        return self.data[netloc]

    def countUrl(self, url):
        netloc = urlparse(url).netloc
        if not netloc in self.data:
            return #this shouldn't happen
        
        self.data[netloc].num_urls += 1

    # print all sub
    def showAllICSSubDomainUrlCounts(self):
        icsSubdomainUrlCounts = dict(zip(self.icssubdomains, [self.data[subdomain].num_urls for subdomain in self.icssubdomains]))
        
        print( "\n".join([ ", ".join((s_item[0], str(s_item[1])))
                        for s_item in sorted( icsSubdomainUrlCounts.items(), key=lambda item: (-1*item[1], item[0]) ) ]) )

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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|scm|img)$")

# English stopwords
stopwords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren\'t", "as", "at",
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
            "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}
subdomainInfo = SubdomainInfo()

# initialize scraper
# blacklist pattern list
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
    print(f"Number of unique urls: {len(unique_urls)}")
    print("longest page:" + longest_page)
    print("ALL ICS SUBDOMAINS AND NUMBER OF URLS CRAWLED")
    subdomainInfo.showAllICSSubDomainUrlCounts()

# saves blacklist pattern list to file path provided
def save_blacklist(blacklistsavepath):
    with open(blacklistsavepath, "w") as f:
        f.write("\n".join(blacklist.keys()))

# Check if there is any repetition in path in the URL, if there is then do not add it to the frontier
def getPathRepeat(urlpath):
    lst = urlpath.split('/')
    dict1 = dict(Counter(lst))
    return [key for key,value in dict1.items() if value > config.path_repeat_threshold]

# Tokenize a string into a list of words and put into token list, also finding the longest page
def tokenizer(string, url):
    global longest_page
    global longest_cnt
    string = string.lower()
    lst = re.split(r'[\s]+', string)

    lst = list(filter(lambda a: not a in stopwords, lst))

    lst = list(filter(lambda a: a != "", lst))

    # Compare this page's content with the longest page
    if len(lst) >= longest_cnt:
        longest_page = url
        longest_cnt = len(lst)
    token_list.extend(lst)
    return lst

def isLowValue(tagCount, tokenCount):
    if tagCount > 3:
        if tokenCount/tagCount < 0.5 and tokenCount < 300:
            return True
    else:
        #tags <html><body><p> are added to pages with no tags
        #assuming text file
        if tokenCount < 300:
            return True
    return False

def textSimilarity(footprint1, footprint2):
    counter = 0
    for i in range(len(footprint1)):
        if footprint1[i] == footprint2[i]:
            counter += 1
    similarity = counter/32

    if similarity >= .80:
        print("Texts are near or exact duplicate!")
    return similarity

def getFootprint(lst):
    dict1 = computeWordFrequencies(lst)
    keys = list(dict1.keys())
    vector = [0] * 32
    for i in keys:
        key = i
        i = format(hash(i), '0>42b')[-32:]                      #hash tokens into 32 bit
    for j in range(len(vector)):
        if i[j] == "1":
            vector[j] = vector[j] + (dict1[key] * int(i[j]))    #if index of key is 1, multiply token freq by 1
        else:
            vector[j] = vector[j] + (dict1[key] * -1)           #if index of key is 1, multiply token freq by -1
    for i in range(len(vector)):
        if vector[i] >= 1:
            vector[i] = 1                                       #if index is positive, set vector[index]=1
        else:
            vector[i] = 0                                       #if index is negative, set vector[index]=0
    return vector

def computeWordFrequencies(alist):
    adict = dict()
    for i in alist:
        if i not in adict.keys():
            adict[i] = 1
        elif i in adict.keys():
            adict[i] = adict[i] + 1
    return adict

def allurlchecks(url):
    return is_valid(url) and not is_blacklisted(url) and not is_trap(url)

def response_invalid(resp):
    return resp.status != 200 or not resp.raw_response or not resp.raw_response.content

def add_url_to_blacklist(url):
    patternstr = f"^{re.escape(url)}$"
    add_pattern_to_blacklist(patternstr)
    
def add_pattern_to_blacklist(pattern, cancel_frontier=False):
    print("BLACKLISTED:", pattern)
    regex = re.compile(pattern)
    blacklist[pattern] = regex
    if cancel_frontier:
        frontier.cancel_urls(regex)

def scraper(url, resp):
    query_dict = {} # A dictionary of urls as keys (no query)
    links = extract_next_links(url, resp)
    return set(sort_by_query(link) for link in links if allurlchecks(link) and subdomainInfo.process_url(link).canFetch(link))


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
        add_url_to_blacklist(url)
        if resp.url != url:
            add_url_to_blacklist(resp.url)
        return set()
    
    # check if redirect is blacklisted
    if resp.url != url and is_blacklisted(resp.url) or not is_valid(resp.url):
        add_url_to_blacklist(url)
        return set()
    
    # check if redirect is a trap
    if resp.url != url and is_trap(resp.url):
        return set()
    
    
    try:
        tree = html.fromstring(resp.raw_response.content) #check if urls are valid
        soup = BS(resp.raw_response.content, "xml")
    except:
        add_url_to_blacklist(url)
        return set()

    # Tokenize the text and add to token list
    text = extract_text(soup)
    tokens = tokenizer(text, url)
    
    if len(soup.findAll("loc")) == 0: #sitemaps are not low value
        # check if page is low value
        tagCount = len(soup.findAll())
        tokenCount = len(tokens)
        if isLowValue(tagCount, tokenCount):
            print("LOW INFO VALUE:", url)
            add_url_to_blacklist(url)
            if resp.url != url:
                add_url_to_blacklist(resp.url)
            return set()

    # check other queries at same subdomain+path
    if "?" in url:
        check_similiar_queries(url, tokens)

    extracted = set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href|.//loc/text()')])
    
    #Add this url to unique urls
    unique_urls.add(url)

    return extracted
    
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

def extract_text(soup):
    # Extract text from the page
    return u" ".join(t.strip() for t in filter(lambda element: not element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] and not isinstance(element, Comment), soup.findAll(text=True)))
# Uses text similiarity to check if url with specfic queries
# is similiar to previously scraped urls. Temp Blacklists those
# when a certain threshold is reached.
def check_similiar_queries(url, tokens):
    global query_dict
    counter_threshold = 3

    #parse url
    parsed = urlparse(url)
    netloc = parsed.netloc
    path = parsed.path
    query = parsed.query

    text = getFootprint(tokens)
    current_key = netloc + path

    #check if url exists in query dict
    if(current_key in query_dict):
        if textSimilarity(text, query_dict[current_key][0]) > 0.8:
            if(query_dict[current_key][1] >= 3):
                temp_blacklist_url = f"{re.escape(urlunsplit((parsed.scheme, netloc, path, '', '')))}.*"
                temporarily_blacklist(temp_blacklist_url)
                del query_dict[current_key]
            else:
                counter = query_dict[current_key][1]
                query_dict[current_key] = [text, counter + 1]
        else:
            query_dict[current_key][1] //= 2
    else:
        query_dict[current_key] = [text, 0]


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
        
        patternstr = f"^{re.escape(urlpart)}.*"

        #delete blacklisted patterns that are included in the new pattern
        todel = []
        for pattern in blacklist:
            if pattern.startswith(patternstr[:-2]):
                todel.append(pattern)
        for p in todel:
            del blacklist[p]
        
        add_pattern_to_blacklist(patternstr, True)

        for r in repeats:
            pattern = f"{re.escape('/'.join(urlpart.split('/')[:-1]))}\\/.*{r}"
            temporarily_blacklist(pattern)
           
        return True
    return False

def temporarily_blacklist(regexpattern):
    print(f"TEMP BLACKLIST {regexpattern}")
    tempregex = re.compile(regexpattern)
    temp_blacklist[regexpattern] = tempregex
    frontier.cancel_urls(tempregex)

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
