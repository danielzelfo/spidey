from bs4 import BeautifulSoup as BS
from bs4.element import Comment
from nltk.stem import PorterStemmer
from urllib.parse import urlparse
import os
import re
import contractions

class HTMLParser:
    def __init__(self):
        # Initialize Porter Stemmer
        self.porterStemmer = PorterStemmer()
        # tokenizing pattern: note: apostrophes are removed
        self.pattern = re.compile(r"[a-z0-9']+")
    
    # Separates string of text into individual tokens, paired with a list of term positions.
    # returns -> list(str, term pos(int))
    # expand contractions
    def tokenize(self, text):
        text = text.lower()
        pos = 0
        for res in self.pattern.finditer(text):
            token = res.group()
            for t in re.split(r"\s|'", contractions.fix(token)):
                yield [t, pos]
                pos += len(t) + 1
    
    # Converts list of token & token positions into a dictionary
    # returns dictionary 
    def tokensAndPositionsToStemDict(self, tokensAndPositions):
        # combine tokens to make list of positions
        tokendict = {}
        for token, position in tokensAndPositions:
            if not token in tokendict:
                tokendict[token] = [position]
            else:
                tokendict[token].append(position)
        
        # stem the unique tokens and combine positions
        stemdict = {}
        for token, positions in tokendict.items():
            stem = self.porterStemmer.stem(token)
            if not stem in stemdict:
                stemdict[stem] = positions
            else:
                stemdict[stem] += positions

        # sort the positions
        for stem in stemdict:
            stemdict[stem].sort()

        return stemdict
    
    # Extracts url content
    def extract_info(self, content, encoding, url):
        soup = BS(content, "html.parser", from_encoding=encoding)
        # if url path ends with .html|.xml|.xhtml|.htm|.php|.aspx|.asp|.jsp
        # or does not have an extension then it is html/xml
        # if the number of tags is 0 then it is not html

        urlpath = urlparse(url).path
        if urlpath.endswith("/") or urlpath.endswith("~"):
            urlpath = urlpath[:-1]
        if soup.find('html') or (not "." in urlpath[-6:] or any( urlpath.endswith(x) for x in [".html",".xml",".xhtml", ".phtml", ".shtml", ".htm",".php",".aspx",".asp",".jsp"])) and len(soup.findAll()) != 0:
            title = soup.title
            if title is None or title.string is None:
                title = os.path.split(urlparse(url).path)[-1].strip()
            else:
                title = title.string.replace("\\u", "").strip().split("\n")[0]
            textcontent = u" ".join(t.strip() for t in filter(lambda element: not element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] and not isinstance(element, Comment), soup.findAll(text=True)))
            return title, textcontent
        else:
            title = os.path.split(urlparse(url).path)[-1].strip()
            return title, content
