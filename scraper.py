import re
from urllib.parse import urlparse, urljoin, urldefrag,
from lxml import html
import re

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

def scraper(url, resp):
    links = sort_by_query(extract_next_links(url, resp))
    
    return [link for link in links if is_valid(link)]

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
    print("extracting from: ", url)
    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content or not is_valid(resp.url):
        return set()
    
    try:
        tree = html.fromstring(resp.raw_response.content) #check if urls are valid
    except:
        return set()

    extracted = set([absolute_url(url, ol) for ol in tree.xpath('.//a[@href]/@href')])

    print("extracted links: ", extracted)
    
    return extracted
    
# sort_by_query will sort querys
# remove any urls with same query parameters
# pointless to run if majority of links have no query parameters

def sort_by_query(links):
    map = {} # Store sorted links
    sorted_links = [] # Return 

    for url in links:
        parsed = urlparse(url)
        # extract/sort query 
        query = parsed.query.split("&")
        query.sort()
        query_string = ""
        # build new query string
        for q in query:
            query_string += q
        print("query_string", query_string)
        # url with sorted query
        new_url = parsed.scheme + parsed.netloc + parsed.path + query_string

        #check if url exists already, if not add to return list
        if new_url not in map:
            map[new_url] = 1
            sorted_links.append(new_url)
    
    return sorted_links



#Pass in a url path
#Detects repeating path trap
# def contains_repeating_path(url_path):
#     map = {}
#     spilt_path = url_path.split("/")[1:]
#     for path in spilt_path:
#         if path in map:
#             return False
#         else:
#             map[path] = 1
#     return True

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
