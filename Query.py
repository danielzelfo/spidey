from nltk.stem import PorterStemmer
from HTMLParser import HTMLParser
from Ranking import Ranking
import json
import datetime
import math

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
                self.docInfoLst.append(docInfo[:2] + [docInfo[3]])#only save title, url, and footprint
        
        self.minlength = 3
        self.stopwords = {'about', 'were', 'having', 'more', 'same', 'for', 'your', 'very', 'up', 'out', 'has', 'again', 'some', 'through', 'all', 'not', 'we', 'during', 'be', 'between', 'until', 'whom', 'theirs', 'few', 'most', 'where', 'such', 'he', 'what', 'those', 'no', 'an', 'let', 'it', 'too', 'you', 'have', 'ours', 'her', 'will', 'who', 'than', 'further', 'after', 'are', 'if', 'was', 'doing', 'our', 'been', 'then', 'into', 'ought', 'the', 'over', 'us', 'while', 'own', 'being', 'his', 'these', 'cannot', 'down', 'in', 'below', 'yourselves', 'their', 'or', 'so', 'him', 'this', 'but', 'they', 'on', 'both', 'once', 'itself', 'them', 'only', 'by', 'there', 'is', 'herself', 'how', 'she', 'did', 'to', 'a', 'themselves', 'which', 'off', 'because', 'against', 'yourself', 'with', 'at', 'its', 'before', 'does', 'that', 'had', 'me', 'i', 'other', 'each', 'hers', 'and', 'as', 'nor', 'under', 'himself', 'am', 'any', 'would', 'from', 'of', 'should', 'must', 'my', 'myself', 'why', 'above', 'when', 'shall', 'could', 'here', 'yours', 'do', 'ourselves'}

        with open("num_documents.txt", "r") as f:
            self.numDocuments = int(f.readline().strip())
        
        self.initializeIndexStemPositions()

    
    def tokenizeStop(self, text):
        tokens = [x[0] for x in self.htmlParser.tokenize(text.strip())]
        newtokens = [t for t in tokens if not t in self.stopwords and len(t) >= self.minlength]
        return newtokens
        
    def initializeIndexStemPositions(self):
        # run through index.txt
        # save positions of stems
        currentPos = 0
        for line in self.indexFile:
            stem = line.split(":")[0]
            self.indexStemPositions[stem] = currentPos
            currentPos += len(line)
    
    # return [[docId1, [positions1]], [docId2, [positions2]], ...]
    def stemDocInfoRetrieve(self, stem):
        documentsInfo = []
        
        if not stem in self.indexStemPositions:
            return documentsInfo
        
        #get positon from self.indexStemPositions
        position = self.indexStemPositions[stem]
        # seek in self.indexFile to that position
        self.indexFile.seek(position)
        
        #skip stem / colon after
        while True:
            c = self.indexFile.read(1)
            if c == ':':
                break
        
        jsonlenstr = ""
        self.indexFile.read(1) #skip [
        while True:
            c = self.indexFile.read(1)
            if not c or c == '\n':
                break
            if c == "]":
                jsonlen = int(jsonlenstr)
                documentsInfo.append(json.loads(self.indexFile.read(jsonlen)))
                jsonlenstr = ""
                c = self.indexFile.read(1) #skip [
                if not c or c == '\n':
                    break
            else:
                jsonlenstr += c
        
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
        
        #rankedDocuments = self.rankDocumentByScore(documentswithAll, documentInfoDictItems)
        # #return first 5 of ranked documents
        #return list(rankedDocuments.keys())

        return documentswithAll

    # Takes in a set of document id numbers and a list of (documentInfoDict) items
    def rankDocumentByScore(self, documentSet, documentInfo):
        documentRank = {}
        # for each word in documentInfo
        for docInfo in documentInfo:
            # for each document in word, check if document is in word posting
            # count the frequency, store into a dictionary
            documents = docInfo[1]
            documentFrequency = len(documents)
            for doc in documents:
                #count frequency (calculate score with tf-idf)
                if doc[0] in documentSet:
                    score = self.tf_idfScore(documentFrequency, Ranking.positionsToRank(doc[1]))
                    if doc[0] in documentRank:
                        documentRank[doc[0]] = documentRank[doc[0]] + score
                    else:
                        documentRank[doc[0]] = score

        documentRank = dict(sorted(documentRank.items(), key = lambda x: x[1], reverse=True))
        
        return documentRank
        
        
    # # tf-idf score:
    # # w(t,d) = (1+log(term freq per document)) * log(N/doc freq)
    # def tf_idfScore(self, docFreq, termFreq):
    #     tf = self.tfScore(termFreq)

    #     idf = self.idfScore(docFreq)

    #     tf_idf = tf * idf

    #     # print(f"tf{tf}, idf{idf}, tf_idf, {tf_idf}")

    #     return tf_idf

    # def tfScore(self, termFreq):
    #     weightScore = 0
    #     if termFreq > 0:
    #         weightScore = 1 + math.log10(termFreq)

    #     return weightScore

    # # docFreq is the the number of documents that contain term
    # def idfScore(self, docFreq):
    #     return math.log10(self.numDocuments/docFreq)

    def printDocumentsInfo(self, docNums):
        print("\n".join(self.docInfoLst[docNum][0]+"\n\t"+self.docInfoLst[docNum][1] for docNum in docNums))
    
    def printQueryResults(self, text):
        # time start
        start_time = datetime.datetime.now()
        res = list(self.ANDboolean(self.docInfoRetrieve(text)))
        # time end
        end_time = datetime.datetime.now()
        print(f"time: {(end_time - start_time).total_seconds() * 1000.0} milliseconds")
        self.printDocumentsInfo(res)