import os
import json
from HTMLParser import HTMLParser

class Indexer:
    def __init__(self):
        self.stem_positions = {}
        self.htmlParser = HTMLParser()
        pass
    
    # filepath ex: aiclub_ics_uci_edu/file.json
    def index(self, filepath):
        # extract data from file
        with open(filepath) as f:
            data = json.load(f)
            content = data["content"]
            encoding = data["encoding"]
            url = data["url"]
        
        # process data
        print("url:", url)

        textContent = self.htmlParser.extract_text(content, encoding, url)
        tokens = self.htmlParser.tokenize(textContent)
        tokenFreq = self.htmlParser.computeWordFrequencies(tokens)

        for token, freq in tokenFreq.items():
            #write_to_disk(token, docum ent,freq)
            pass
             

            

        # parse
        # stem
        # ...
        # write to disk
        pass
    
    def write_to_disk(self, stem, document, documentposition, terms, frequency):
        # open the disk file
        # check if stem was indexed before
        # if it is
        #     append to end of line ", {document, documentposition, terms, frequency}"
        # if not, add to end of file
        # format: "stem: {document, documentposition, terms, frequency}"
        
        pass