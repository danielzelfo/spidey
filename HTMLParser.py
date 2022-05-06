from bs4 import BeautifulSoup as BS
from bs4.element import Comment
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import re
from urllib.parse import urlparse

class HTMLParser:
    def __init__(self):
        # Initialize Porter Stemmer
        self.porterStemmer = PorterStemmer()
        # Initlize tokenizer from nltk
        self.tokenizer = RegexpTokenizer(r"[a-z0-9]+")
        
    # Separates string of text into individual tokens, paired with a list of term positions.
    # returns -> list(str, term pos(int))
    def tokenize(self, text):
        text = text.lower()
        return [[text[span[0]:span[1]], span[0]] for span in self.tokenizer.span_tokenize()]
    
    # Converts list of token & token positions into a dictionary
    # returns dictionary 
    def tokensAndPositionsToDict(self, tokensAndPositions):
        thedict = {}
        for token, position in tokensAndPositions:
            if not token in thedict:
                thedict[token] = [position]
            else:
                thedict[token].append(position)
        return thedict
    
    # Extracts url content
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
