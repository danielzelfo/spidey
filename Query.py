from nltk.stem import PorterStemmer
from HTMLParser import HTMLParser
import json
import datetime
import math

class Query:
    def __init__(self):
        self.indexStemPositions = { }
        self.bigramStemPositions = { }
        self.indexFile = open("index.txt", "r")
        self.bigramIndexFile = open("bigram_index.txt", "r")
        self.porterStemmer = PorterStemmer()
        self.docInfoLst = []
        self.htmlParser = HTMLParser()
        self.numResults = 5

        with open("docInfo.txt", "r") as f:
            for line in f:
                docInfo = json.loads(line.strip())
                self.docInfoLst.append(docInfo[:2] + [docInfo[3]])#only save title and url
        
        self.minlength = 3
        self.stopwords = {'about', 'were', 'having', 'more', 'same', 'for', 'your', 'very', 'up', 'out', 'has', 'again', 'some', 'through', 'all', 'not', 'we', 'during', 'be', 'between', 'until', 'whom', 'theirs', 'few', 'most', 'where', 'such', 'he', 'what', 'those', 'no', 'an', 'let', 'it', 'too', 'you', 'have', 'ours', 'her', 'will', 'who', 'than', 'further', 'after', 'are', 'if', 'was', 'doing', 'our', 'been', 'then', 'into', 'ought', 'the', 'over', 'us', 'while', 'own', 'being', 'his', 'these', 'cannot', 'down', 'in', 'below', 'yourselves', 'their', 'or', 'so', 'him', 'this', 'but', 'they', 'on', 'both', 'once', 'itself', 'them', 'only', 'by', 'there', 'is', 'herself', 'how', 'she', 'did', 'to', 'a', 'themselves', 'which', 'off', 'because', 'against', 'yourself', 'with', 'at', 'its', 'before', 'does', 'that', 'had', 'me', 'i', 'other', 'each', 'hers', 'and', 'as', 'nor', 'under', 'himself', 'am', 'any', 'would', 'from', 'of', 'should', 'must', 'my', 'myself', 'why', 'above', 'when', 'shall', 'could', 'here', 'yours', 'do', 'ourselves'}

        with open("num_documents.txt", "r") as f:
            self.numDocuments = int(f.readline().strip())
        
        self.initializeIndexStemPositions()
        self.initializeBigramIndexStemPositions()

    def tokenizeStop(self, text):
        tokens = [x[0] for x in self.htmlParser.tokenize(text.strip())]
        newtokens = [t for t in tokens if not t in self.stopwords and len(t) >= self.minlength]
        return newtokens
    
    def tokenizeBigramStop(self, text):
        #passes if 1st or 2nd token is not a stop word, passes condition
        def passcond(t):
            ts = t.split()
            return not (ts[0] in self.stopwords or ts[1] in self.stopwords)
        tokens = [x[0] for x in self.htmlParser.bigram_tokenize(text.strip())]
        newtokens = [t for t in tokens if passcond(t)]
        return newtokens
        
    def initializeIndexStemPositions(self):
        # run through index.txt
        # save positions of stems
        currentPos = 0
        for line in self.indexFile:
            stem = line.split(":")[0]
            self.indexStemPositions[stem] = currentPos
            
            #time.sleep(1)
            currentPos += len(line)
    
    def initializeBigramIndexStemPositions(self):
        # run through bigram_index.txt
        # save positions of stems
        currentPos = 0
        for line in self.bigramIndexFile:
            stem = line.split(":")[0]
            self.bigramStemPositions[stem] = currentPos
            currentPos += len(line)

    # return [[docId1, [positions1]], [docId2, [positions2]], ...]
    def stemDocInfoRetrieve(self, stem, indexFile = None, stemPositions = None):        
        if indexFile is None:
            indexFile = self.indexFile
        
        if stemPositions is None:
            stemPositions = self.indexStemPositions
        
        documentsInfo = []
        
        if not stem in stemPositions:
            return documentsInfo
        
        #get positon from index stem positions
        position = stemPositions[stem]
        # seek in self.indexFile to that position
        indexFile.seek(position)
        
        #skip stem / colon after
        while True:
            c = indexFile.read(1)
            if c == ':':
                break

        jsonlenstr = ""
        indexFile.read(1) #skip [
        
        while True:
            c = indexFile.read(1)
            if not c or c == '\n':
                break
            if c == "]":
                jsonlen = int(jsonlenstr)
                documentsInfo.append(json.loads(indexFile.read(jsonlen)))
                
                jsonlenstr = ""
                c = indexFile.read(1) #skip [
                if not c or c == '\n':
                    break
            else:
                jsonlenstr += c
        
        return documentsInfo

    def stemBigram(self, token):
        return " ".join([self.porterStemmer.stem(t) for t in token.split()])

    def docInfoRetrieve(self, text, tokenizeFunction=None, stemFunction=None, indexFile = None, stemPositions = None):
        
        if tokenizeFunction is None:
            tokenizeFunction = self.tokenizeStop

        if stemFunction is None:
            stemFunction = self.porterStemmer.stem
        
        # tokenize
        # remove stop words
        splitText = tokenizeFunction(text)
        

        documentInfoDict = {}
        
        for word in splitText:
            stem = stemFunction(word)
            documentInfoDict[stem] = self.stemDocInfoRetrieve(stem, indexFile, stemPositions)
        
        
        return documentInfoDict
    
    def documentRetrieval(self, text):
        documentInfoDict = self.docInfoRetrieve(text)
        #("after retrieval: ", documentInfoDict)
        if len(documentInfoDict) == 0:
            return []

        documentInfoDictItems = list(documentInfoDict.items())

        
        cutoffPoint = 100
        maxCutofPoint = 1600
        lengthneeded = self.numResults
        while True:
            documentswithAll = [[docInfo[0], docInfo[2]] for docInfo in documentInfoDictItems[0][1][:cutoffPoint]]
            
            for stemDocInfo in documentInfoDictItems[1:]:
                documentswithAll = self.intersect(documentswithAll, [[docInfoItem[0], docInfoItem[2]] for docInfoItem in stemDocInfo[1][:cutoffPoint]], lambda x: x[0])
            
            if cutoffPoint >= maxCutofPoint:
                break

            if len(documentswithAll) < lengthneeded:
                cutoffPoint*=2
                continue
            
            break

        # here we have all the docs with all the words
        # adjust score based on bigram

        return list(documentswithAll)
    
    def bigramscoring(self, documentswithAll, queryText):
        setOfAllPrev = set(x[0] for x in documentswithAll)
        
        cutoffPoint = 999
        documentInfoDict = self.docInfoRetrieve(queryText, self.tokenizeBigramStop, self.stemBigram, self.bigramIndexFile, self.bigramStemPositions)
        documentInfoDictItems = list(documentInfoDict.items())
        #get set of bigram documents, intersect regular document index with bigram documents into bigramdocumentid
        #check if regular docs are in bigram doc- if so, add score to it
        for i in range(len(documentInfoDict)):
            bigramdocuments = [[docInfo[0], docInfo[2]] for docInfo in documentInfoDictItems[i][1][:cutoffPoint]]
            
            bigramdocumentsDict = {x[0]: x[1] for x in bigramdocuments}
            bigramdocumentsIds = set(x[0] for x in bigramdocuments)
            bigramdocumentsIds.intersection_update(setOfAllPrev)

            for doc in documentswithAll:
                if doc[0] in bigramdocumentsIds:
                    doc[1] += bigramdocumentsDict[doc[0]]          #add tf-idf score if it has a bigram

    def find(self, lst, value, key):
        for i in lst:
            if key(i) == key(value):
                return i
        return None

    # make list unique -- preserve order
    def unique(self, lst, key):
        checkseen = set()
        newlst = []
        for i in lst:
            if key(i) not in checkseen:
                newlst.append(i)
            checkseen.add(key(i))
        return newlst

    def intersect(self, lst1, lst2, key):
        lst3 = []
        lst1 = self.unique(lst1, key=lambda x: x[0])
        lst2 = self.unique(lst2, key=lambda x: x[0])
        for value in lst1:
            found = self.find(lst2, value, key)
            if found:
                lst3.append([value[0], value[1] + found[1]])
        return lst3
    
    def cosineSim(self, query, documentswithAll):
        documentInfoDict = self.docInfoRetrieve(query)
        # documentInfoDictItems = list(documentInfoDict.items())
        scores = {}
        
        query = query.split(" ")
        # new stemInfo{'stem', [[doc number, [postions], tfidf_score]}
        for stem in documentInfoDict:
            documents = documentInfoDict[stem]
            
            df = len(documents)
            for posting in documents:
                term_frequency = len(posting[1])
                doc_id = posting[0]
                tf_idf = posting[2]
                qFreq = self.queryFreq(query, stem)
                qScore = self.tf_idfScore(df,qFreq)
                # calculate score
                
                if doc_id in scores:
                    scores[doc_id] += qScore * posting[2]
                else:
                    scores[doc_id] = qScore * posting[2]
                
        for doc_id, score in scores.items():
            doc_len = math.log10(self.docInfoLst[doc_id][2])
            scores[doc_id] = round(scores[doc_id] / doc_len,3)

        for doc in documentswithAll:
            if doc[0] in scores:
                doc[1] = scores[doc[0]] 
        
        return documentswithAll

    def queryFreq(self, query, word):
        count = 0
        for q in query:
            
            if self.porterStemmer.stem(q) == word:
                count += 1
        return count
    # tf-idf score:
    # w(t,d) = (1+log(term freq per document)) * log(N/doc freq)
    def tf_idfScore(self, docFreq, termFreq):
        tf = self.tfScore(termFreq)

        idf = self.idfScore(docFreq)

        tf_idf = tf * idf

        return tf_idf

    def tfScore(self, termFreq):
        weightScore = 0
        if termFreq > 0:
            weightScore = 1 + math.log10(termFreq)

        return weightScore

    # docFreq is the the number of documents that contain term
    def idfScore(self, docFreq):
        return math.log10(self.numDocuments/docFreq)

    def printDocumentsInfo(self, docNums):
        print("\n".join(self.docInfoLst[docNum][0]+"\n\t"+self.docInfoLst[docNum][1] for docNum in docNums))
    
    def printQueryResults(self, text):
        # time start
        start_time = datetime.datetime.now()
        res = self.documentRetrieval(text)
        self.bigramscoring(res, text)
        res = self.cosineSim(text, res)
        
        res = sorted(res, key=lambda x: x[1], reverse=True)[:self.numResults]
        # time end
        end_time = datetime.datetime.now()
        print(f"time: {(end_time - start_time).total_seconds() * 1000.0} milliseconds")
        self.printDocumentsInfo([r[0] for r in res])