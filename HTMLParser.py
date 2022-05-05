from bs4 import BeautifulSoup as BS
from bs4.element import Comment
from nltk.stem import PorterStemmer
import re
from urllib.parse import urlparse

class HTMLParser:
    def __init__(self):
        self.token_pattern = "[a-zA-Z0-9]+"
        self.porterStemmer = PorterStemmer()
        pass

    def tokenize(self, text):
        text = text.lower()
        lst = [self.porterStemmer.stem(token) for token in re.findall(self.token_pattern, text)]
        return lst
    
    def computeWordFrequencies(self, alist):
        adict = {}
        for stem in alist:
            if not stem in adict:
                adict[stem] = 1
            else:
                adict[stem] += 1
        return adict
        
    def extract_text(self, content, encoding, url):
        soup = BS(content, "html.parser", from_encoding=encoding)
        # if url path ends with .html|.xml|.xhtml|.htm|.php|.aspx|.asp|.jsp
        # or does not have an extension then it is html/xml
        # if the number of tags is 0 then it is not html

        urlpath = urlparse(url).path
        if urlpath.endswith("/") or urlpath.endswith("~"):
            urlpath = urlpath[:-1]
        if soup.find('html') or (not "." in urlpath[-6:] or any( urlpath.endswith(x) for x in [".html",".xml",".xhtml", ".phtml", ".shtml", ".htm",".php",".aspx",".asp",".jsp"])) and len(soup.findAll()) != 0:
            return u" ".join(t.strip() for t in filter(lambda element: not element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] and not isinstance(element, Comment), soup.findAll(text=True)))
        else:
            return content