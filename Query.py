from nltk.stem import PorterStemmer
from HTMLParser import HTMLParser
from nltk.tokenize import RegexpTokenizer
import json
import datetime
import contractions
import re

class Query:
    def __init__(self):
        self.indexStemPositions = { }
        self.indexFile = open("index.txt", "r")
        self.porterStemmer = PorterStemmer()
        self.docInfoLst = []
        self.htmlParser = HTMLParser()
        with open("docInfo.txt", "r") as f:
            for line in f:
                docInfo = json.loads(line.strip())
                self.docInfoLst.append(docInfo[:2])#only save title and url
        
        self.minlength = 3
        self.stopwords = {'about', 'were', 'having', 'more', 'same', 'for', 'your', 'very', 'up', 'out', 'has', 'again', 'some', 'through', 'all', 'not', 'we', 'during', 'be', 'between', 'until', 'whom', 'theirs', 'few', 'most', 'where', 'such', 'he', 'what', 'those', 'no', 'an', 'let', 'it', 'too', 'you', 'have', 'ours', 'her', 'will', 'who', 'than', 'further', 'after', 'are', 'if', 'was', 'doing', 'our', 'been', 'then', 'into', 'ought', 'the', 'over', 'us', 'while', 'own', 'being', 'his', 'these', 'cannot', 'down', 'in', 'below', 'yourselves', 'their', 'or', 'so', 'him', 'this', 'but', 'they', 'on', 'both', 'once', 'itself', 'them', 'only', 'by', 'there', 'is', 'herself', 'how', 'she', 'did', 'to', 'a', 'themselves', 'which', 'off', 'because', 'against', 'yourself', 'with', 'at', 'its', 'before', 'does', 'that', 'had', 'me', 'i', 'other', 'each', 'hers', 'and', 'as', 'nor', 'under', 'himself', 'am', 'any', 'would', 'from', 'of', 'should', 'must', 'my', 'myself', 'why', 'above', 'when', 'shall', 'could', 'here', 'yours', 'do', 'ourselves'}

        self.initializeIndexStemPositions()

    
    def tokenizeStop(self, text):
        self.htmlParser.tokenizer = RegexpTokenizer(r"[a-z0-9']+")
        tokens = [x[0] for x in self.htmlParser.tokenize(text.strip())]
        newtokens = []
        for token in tokens:
            for t in re.split(r"\s|'", contractions.fix(token)):
                if not t in self.stopwords and len(t) >= self.minlength:
                    newtokens.append(t)
        return newtokens
        
    def initializeIndexStemPositions(self):
        # run through index.txt
        # save positions of stems
        currentPos = 0
        for line in self.indexFile:
            stem = line.split(":")[0]
            self.indexStemPositions[stem] = currentPos
            currentPos += len(line)

    def stemDocInfoRetrieve(self, stem):
        documentsInfo = []
        
        if not stem in self.indexStemPositions:
            return documentsInfo
        
        #get positon from self.indexStemPositions
        position = self.indexStemPositions[stem]
        # seek in self.indexFile to that position
        self.indexFile.seek(position)
        # read line
        line = self.indexFile.readline().strip()
        documents = line[len(line.split(":")[0])+1:]

        # Read [length to read]{doc1 json}[length to read]{doc2 json}
        curidx = 0
        while curidx < len(documents):
            jsonlenstr = ""
            for char in documents[curidx+1:]:
                if char == "]":
                    break              
                jsonlenstr += char
            jsonlen = int(jsonlenstr)
            documentsInfo.append(json.loads(documents[curidx + len(jsonlenstr) + 2 : curidx + len(jsonlenstr) + 2 + jsonlen]))
            curidx += len(jsonlenstr) + 2 + jsonlen
        
        return documentsInfo
    
    def docInfoRetrieve(self, text):
        # tokenize
        # remove stop words
        splitText = self.tokenizeStop(text)

        documentInfoDict = {}
        
        for word in splitText:
            stem = self.porterStemmer.stem(word)
            documentInfoDict[stem] = self.stemDocInfoRetrieve(stem)
        
        return documentInfoDict
            
    def ANDboolean(self, documentInfoDict):
        if len(documentInfoDict) == 0:
            return set()
        documentInfoDictItems = list(documentInfoDict.items())

        documentswithAll = set([docInfo[0] for docInfo in documentInfoDictItems[0][1]])
        for stemDocInfo in documentInfoDictItems[1:]:
            documentswithAll = documentswithAll.intersection(docInfoItem[0] for docInfoItem in stemDocInfo[1])
        
        return documentswithAll


    def rankDocumentByFrequency(self, documentSet):
        
        for document in documentSet:
            pass
        pass
        

    def printDocumentsInfo(self, docNums):
        print("\n".join(self.docInfoLst[docNum][0]+"\n\t"+self.docInfoLst[docNum][1] for docNum in docNums))
    
    def printQueryResults(self, text):
        self.printDocumentsInfo(list(self.ANDboolean(self.docInfoRetrieve(text)))[:5])