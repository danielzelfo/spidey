import re
from urllib.parse import urlparse, urljoin, urldefrag, urlunsplit
from lxml import html
from collections import Counter
import os
from utils.download import download
import time
from bs4 import BeautifulSoup as BS
from bs4.element import Comment
import json
import pickle
import signal

#urllib.robotparser modified to give Allow entries higher precedence 
import robotparser

# SIGINT handler to save the data used by the scraper and exit gracefully
def siginthandler(signum, fname):
    print("\nCLICKED CTRL-C")
    print_info()
    print("[...] closing and joining threads")
    for worker in crawler.workers:
        worker.exit = True
    crawler.join()
    print("[...] syncing shelf")
    crawler.frontier.save.sync()
    print("[...] saving scraper data")
    save()
    print("[...] exiting")
    exit(1)

signal.signal(signal.SIGINT, siginthandler)


prevURL = {}
pageFootprints = {}
blacklist = {}
temp_blacklist = {}
unique_url_count = 0
query_dict = {}
token_counts = {}
longest_page = ""
longest_cnt = 0
previouspage = None
crawler = None

# contains information about all visited subdomains
class SubdomainInfo:
    # each subdomain has an entry (SubdomainEntry) saved in the self.data of SubdomainInfo
    # each entry contains the number of urls discovered while crawling and the robots.txt parser object
    # the robots.txt parser caches the robots.txt file for the domain and can be used to verify that a url on the subdomain can be crawled
    class SubdomainEntry:
        def __init__(self, netloc):
            self.netloc = netloc
            self.robots = None
            self.num_urls = 0
        
        def canFetch(self, url):
            return self.robots is None or self.robots.can_fetch('*', url)

        # give a url on the subdomain
        # download the robots.txt file and parse it
        # if the robots.txt file contains a sitemap of type txt, download it and add each of the urls in it to the frontier
        # if the robots.txt file contains a sitemap that does not have a .txt file extension, then add it to the frontier
        def process_robots(self, url):
            robotsurl = url.split(self.netloc)[0] + self.netloc+"/robots.txt"

            time.sleep(crawler.config.time_delay)
            resp = download(robotsurl, crawler.config)

            if response_invalid(resp) or not is_valid(resp.url):
                return
            
            self.num_urls += 1

            self.robots = robotparser.RobotFileParser()
            self.robots.parse(resp.raw_response.content.decode("utf-8").splitlines())
            
            for sitemapurl in self.robots.site_maps():
                print("ADDED SITEMAP:", sitemapurl)

                if sitemapurl.lower().endswith(".txt"):
                    time.sleep(crawler.config.time_delay)
                    resp = download(sitemapurl, crawler.config)
                    if not (response_invalid(resp) or not is_valid(resp.url)):
                        self.num_urls += 1
                        for fromsitemaptxt in resp.raw_response.content.splitlines():
                            crawler.frontier.add_url(fromsitemaptxt)
                elif allurlchecks(sitemapurl):
                    crawler.frontier.add_url(sitemapurl)

    def __init__(self):
        self.data = {}
        self.icssubdomains = []
    
    # given a url, check if the subdomain has been encountered before
    # if it has not, then create a new subdomain entry and process the robots.txt file if it exists
    # if applicable, append the subdomain to the list of subdomains in ics.uci.edu
    # finally, return the subdomain entry
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

    # increment the counter for the number of urls discovered by the subdomain containing the given url
    def countUrl(self, url):
        netloc = urlparse(url).netloc
        if not netloc in self.data:
            return #this shouldn't happen
        
        self.data[netloc].num_urls += 1

    # print all subdomains on ics.uci.edu sorted by the subdomain string alphabetically
    def showAllICSSubDomainUrlCounts(self):
        print( "\n".join([ ", ".join(s_item)
                        for s_item in sorted( zip(self.icssubdomains, [str(self.data[subdomain].num_urls) for subdomain in self.icssubdomains]) ) ]) )

# scheme and netloc patterns for filtering out invalid urls
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
# token pattern
token_pattern = r"[a-zA-Z'-]{2,}"
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

# the subdomain info object
subdomainInfo = SubdomainInfo()

# initialize scraper
# initializes all the global variables
# SubdomainInfo is saved as a serializing object. It is unpickled from the file specified in config.ini
# All other data is saved in a JSON file. The compiled regex patterns cannot be saved in a JSON file.
# Their string patterns are saved, and they are recompiled when the scraper is initialized
def init(tcrawler):
    global crawler, blacklist, temp_blacklist, unique_url_count, query_dict, token_counts, longest_page, longest_cnt, subdomainInfo, prevURL, pageFootprints, previouspage
    crawler = tcrawler

    if os.path.exists(crawler.config.blacklist_file):
        with open(crawler.config.blacklist_file, "r") as f:
            blacklist = json.load(f)
        for reason in blacklist:
            blacklist[reason] = {pattern: re.compile(pattern) for pattern in blacklist[reason]}
    
    if os.path.exists(crawler.config.temp_scraper_info):
        with open(crawler.config.temp_scraper_info, "r") as f:
            data = json.load(f)
            temp_blacklist = {pattern: re.compile(pattern) for pattern in data["temp_blacklist"]}
            unique_url_count = data["unique_url_count"]
            query_dict = data["query_dict"]
            prevURL = data["prevURL"]
            pageFootprints = data["pageFootprints"]
            token_counts = data["token_counts"]
            longest_page = data["longest_page"]
            longest_cnt = data["longest_cnt"]
            previouspage = data["previouspage"]
    
    if os.path.exists(crawler.config.temp_scraper_subdomain_info):
        with open(crawler.config.temp_scraper_subdomain_info, "rb") as f:
            subdomainInfo = pickle.load(f)

# find the 50 most common tokens in the token_counts dictionary
def mostcommontokens():
    mostcommon = set()
    token_count_items = list(token_counts.items())
    for _ in range(50):
        most = -1
        for i in range(len(token_count_items)):
            if (most == -1 or token_count_items[i][1] > token_count_items[most][1]) and not i in mostcommon:
                most = i
        mostcommon.add(most)
    return sorted([token_count_items[idx] for idx in mostcommon], key=lambda x: x[1], reverse=True)

# prints report information
# most common urls, unique urls, longest page, number of subdomain crawled
def print_info():
    print(mostcommontokens())
    print(f"Number of unique urls: {unique_url_count}")
    print("longest page:" + longest_page)
    print("ALL ICS SUBDOMAINS AND NUMBER OF URLS CRAWLED")
    subdomainInfo.showAllICSSubDomainUrlCounts()

# save all the global variables to disk
# the SubdomainInfo instance is serialized using the pickle library
# the temporary blacklist pattern is 
# everything except blacklist is deleted when the crawler is launched with the restart flag
# the permanent blacklist contains different reasons for blacklisting, which are the keys in the dictionary
# the value for each reason key is another dictionary with string regex patterns as keys and them compiled as the values
# Only the string regex are saved to disk (not the compiled ones), and they are recompiled when the program launches again
def save():
    if crawler is None:
        return
    
    with open(crawler.config.blacklist_file, "w") as f:
        json.dump({reason: list(blacklist[reason].keys()) for reason in blacklist}, f, indent=4)
    
    tempdict = {
        "temp_blacklist": list(temp_blacklist.keys()),
        "unique_url_count": unique_url_count,
        "query_dict": query_dict,
        "prevURL": prevURL,
        "pageFootprints": pageFootprints,
        "token_counts": token_counts,
        "longest_page": longest_page,
        "longest_cnt": longest_cnt,
        "previouspage": previouspage
    }
    with open(crawler.config.temp_scraper_info, "w") as f:
        json.dump(tempdict, f)
    
    with open(crawler.config.temp_scraper_subdomain_info, "wb") as f:
        pickle.dump(subdomainInfo, f)

# Check if there is any repetition in path in the URL
# return a list of paths that are repeated more than the threshold specified in config.ini
# this is used to permanently ban url patterns starting with the url up to the first repeating path
def getPathRepeat(urlpath):
    lst = urlpath.split('/')
    dict1 = dict(Counter(lst))
    return [key for key,value in dict1.items() if value > crawler.config.path_repeat_threshold]

# Tokenize a string into a list of words and put into token list, also finding the longest page
def tokenizer(string, url):
    global longest_page, longest_cnt
    
    #lowercase string
    string = string.lower()
    
    # Create list of tokens matching token pattern
    lst = re.findall(token_pattern, string)

    # Remove stopwords from list
    lst = list(filter(lambda a: a != "" and not a in stopwords, lst))

    # Compare this page's content with the longest page
    current_length = len(lst)
    if current_length >= longest_cnt:
        longest_page = url
        longest_cnt = current_length
    
    for token in lst:
        if not token in token_counts:
            token_counts[token] = 0
        token_counts[token] += 1
    
    return lst

# Compares number of tags with number of tokens
# Considers page low value if ratio of tokens to tag is less than a set amount
# or if tokens is less than a certain value
# Returns bool
def isLowValue(tagCount, tokenCount):
    if tagCount > 3:
        if tokenCount/tagCount < 0.5 and tokenCount < 150:
            return True
    else:
        #assuming text file
        if tokenCount < 150:
            return True
    return False


def textSimilarity(footprint1, footprint2):
    counter = 0
    length = len(footprint1[0])
    for i in range(length):
        if footprint1[0][i] == footprint2[0][i]:
            counter += 1
    similarity = counter/length
    similaritylength = min(footprint1[1],footprint2[1])/max(footprint1[1],footprint2[1])
    if similarity >= .90 and similaritylength > .90:
        print("Texts are near or exact duplicate!")
    return similarity, similaritylength

def getFootprint(lst):
    dict1 = computeWordFrequencies(lst)
    keys = list(dict1.keys())
    vector = [0] * 128
    for i in keys:
        key = i
        i = format(hash(i), '0>128b')[-128:]                      #hash tokens into 128 bit
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
    return ("".join([str(z) for z in vector]), len(lst))

# Creates a frequency dictionary with tokens as keys, frequencies as values
def computeWordFrequencies(alist):
    adict = dict()
    for i in alist:
        if i not in adict.keys():
            adict[i] = 1
        elif i in adict.keys():
            adict[i] = adict[i] + 1
    return adict

# Performs a series of checks to see if url is valid, is blacklisted, or is a trap.
def allurlchecks(url):
    return is_valid(url) and not is_blacklisted(url) and not is_trap(url)

# Checks if response contains valid response code/content
def response_invalid(resp):
    return resp.status != 200 or not resp.raw_response or not resp.raw_response.content

# Add a new URL to blacklist
def add_url_to_blacklist(url, reason):
    patternstr = f"^{re.escape(url)}$"
    add_pattern_to_blacklist(patternstr, reason=reason)

# Saves a url patter to blacklist and cancels out blacklisted urls from froniter
def add_pattern_to_blacklist(pattern, cancel_frontier=False, reason="none"):
    print("BLACKLISTED:", pattern, f"for reason [{reason}]")
    if not reason in blacklist:
        blacklist[reason] = {}
    regex = re.compile(pattern)
    blacklist[reason][pattern] = regex
    if cancel_frontier:
        crawler.frontier.cancel_urls(regex)


# if given url and resp are valid
# scraper will extract and return urls 
# that contain "high value information"
def scraper(url, resp):
    links = extract_next_links(url, resp)
    outlinks = set(sort_by_query(link) for link in links if allurlchecks(link) and subdomainInfo.process_url(link).canFetch(link))
    for outlink in outlinks:
        prevURL[outlink] = url
    return outlinks


def absolute_url(page_url, outlink_url):
    # join urls | note: if outlink_url is an absolute url, that url is used
    newurl = urljoin(page_url, outlink_url)
    # remove fragment
    return urldefrag(newurl)[0]

def extract_next_links(url, resp):
    global previouspage
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if response_invalid(resp):
        add_url_to_blacklist(url, "bad url")
        if resp.url != url:
            add_url_to_blacklist(resp.url, "bad url")
        return set()
    
    # check if redirect is blacklisted
    if resp.url != url and (is_blacklisted(resp.url) or not is_valid(resp.url)):
        add_url_to_blacklist(url, "bad url")
        return set()
    
    # check if redirect is a trap
    if resp.url != url and is_trap(resp.url):
        return set()
    
    try:
        tree = html.fromstring(resp.raw_response.content) #check if urls are valid
    except:
        return set()
    
    if tree.xpath("count(//loc)") == 0: # not sitemap check
        soup = BS(resp.raw_response.content, "html.parser", from_encoding="iso-8859-1")

        tagCount = len(soup.findAll())

        # Tokenize the text and add to token list
        # Note: this only works for html.parser which does not add any tags
        text = str(soup) if url.endswith(".txt") or tagCount == 0 else extract_text(soup)
        tokens = tokenizer(text, url)

        # check if page is low value
        tokenCount = len(tokens)
        if isLowValue(tagCount, tokenCount):
            add_url_to_blacklist(url, "low info value")
            if resp.url != url:
                add_url_to_blacklist(resp.url, "low info value")
            return set()

        #Add this url to unique urls
        unique_url_count += 1
        #count url in subdomain
        subdomainInfo.countUrl(url)
        

        text = getFootprint(tokens)

        
        # check other queries at same subdomain+path
        if "?" in url:
            check_similiar_queries(url, text)
        #check if footprint is similar to prev page
        
        # if the url has a page that linked it and it or the page that linked it are not query pages, then check their similarity
        # if they are more similar than the similarity threshold, then do not extract any links from the current url
        prev = None
        if url in prevURL:
            prev = prevURL[url]
            if (not "?" in url or not "?" in prev) and prev in pageFootprints:
                sim = textSimilarity(text, pageFootprints[prev])
                if sim[0] > 0.9 and sim[1] > 0.9:
                    print("SIMILAR PAGE to linked from", url, prev, sim)
                    return set()
        
        # if the previous page that the crawler checked is not the page that linked the current page
        # then check their similarity
        if not previouspage is None and previouspage != prev \
                and (not "?" in url or not "?" in previouspage) \
                and (previouspage in pageFootprints):
            sim = textSimilarity(text, pageFootprints[previouspage])
            if sim[0] > 0.9 and sim[1] > 0.9:
                print("SIMILAR PAGE to previous", url, previouspage, sim)
                return set()

        previouspage = url
        pageFootprints[url] = text
    else:
        #Add this url to unique urls
        unique_url_count += 1
        #count url in subdomain
        subdomainInfo.countUrl(url)

        previouspage = None

        
    #Join relative and absolute paths
    extracted = set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href|.//loc/text()')])
    
    

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
def check_similiar_queries(url, text):
    counter_threshold = 3

    #parse url
    parsed = urlparse(url)
    netloc = parsed.netloc
    path = parsed.path
    query = parsed.query

    current_key = netloc + path

    #check if url exists in query dict
    if(current_key in query_dict):
        #get similarity of current text and previous stored text
        similarity = textSimilarity(text, query_dict[current_key][0])
        # if similarity exceeds threshold/counter of previous similiar queries
        # temp blacklist url
        # otherwise reduce counter
        if similarity[0] > 0.9 and similarity[1] > 0.9:
            if(query_dict[current_key][1] >= counter_threshold):
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
    for reason in blacklist:
        for pattern in blacklist[reason]:
            if blacklist[reason][pattern].match(url):
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
        if "repeating path trap" in blacklist:
            todel = []
            for pattern in blacklist["repeating path trap"]:
                if pattern.startswith(patternstr[:-2]):
                    todel.append(pattern)
            for p in todel:
                del blacklist["repeating path trap"][p]
        
        add_pattern_to_blacklist(patternstr, True, "repeating path trap")

        for r in repeats:
            pattern = f"{re.escape('/'.join(urlpart.split('/')[:-1]))}\\/.*{r}"
            temporarily_blacklist(pattern)
           
        return True
    return False

# Adds a regex pattern into temp blacklist
# cancels all urls that match regex
def temporarily_blacklist(regexpattern):
    print(f"TEMP BLACKLIST {regexpattern}")
    tempregex = re.compile(regexpattern)
    temp_blacklist[regexpattern] = tempregex
    crawler.frontier.cancel_urls(tempregex)

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
