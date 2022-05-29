from nltk.stem import PorterStemmer
from regex import D
from HTMLParser import HTMLParser
import json
import datetime
import math


# Query class processes a string of input text
# Uses different scoring/ranking methods to determine the most relevant urls
# from indexed urls.
# Scores depend tf-idf weighting, url content sizes, bi-gram scoring and cosine scoring.

class Query:
    def __init__(self):
        self.indexStemPositions = { } 
        self.bigramStemPositions = { }
        self.indexFile = open("index.txt", "r")
        self.bigramIndexFile = open("bigram_index.txt", "r")
        self.porterStemmer = PorterStemmer()
        self.docInfoLst = []
        self.htmlParser = HTMLParser()

        # number of results to show
        self.numResults = 10

        with open("docInfo.txt", "r") as f:
            for line in f:
                docInfo = json.loads(line.strip())
                self.docInfoLst.append(docInfo[:2] + [docInfo[3]]) # [title, url, token count]
        
        self.minlength = 2
        self.STOPWORDS = {'about', 'were', 'having', 'more', 'same', 'for', 'your', 'very', 'up', 'out', 'has', 'again', 'some', 'through', 'all', 'not', 'we', 'during', 'be', 'between', 'until', 'whom', 'theirs', 'few', 'most', 'where', 'such', 'he', 'what', 'those', 'no', 'an', 'let', 'it', 'too', 'you', 'have', 'ours', 'her', 'will', 'who', 'than', 'further', 'after', 'are', 'if', 'was', 'doing', 'our', 'been', 'then', 'into', 'ought', 'the', 'over', 'us', 'while', 'own', 'being', 'his', 'these', 'cannot', 'down', 'in', 'below', 'yourselves', 'their', 'or', 'so', 'him', 'this', 'but', 'they', 'on', 'both', 'once', 'itself', 'them', 'only', 'by', 'there', 'is', 'herself', 'how', 'she', 'did', 'to', 'a', 'themselves', 'which', 'off', 'because', 'against', 'yourself', 'with', 'at', 'its', 'before', 'does', 'that', 'had', 'me', 'i', 'other', 'each', 'hers', 'and', 'as', 'nor', 'under', 'himself', 'am', 'any', 'would', 'from', 'of', 'should', 'must', 'my', 'myself', 'why', 'above', 'when', 'shall', 'could', 'here', 'yours', 'do', 'ourselves'}
        self.stopwords = self.STOPWORDS
        
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
        
        
        return documentInfoDict# 
    
    # Function to find documents with all tokens in user query
    def ANDBoolean(self, documentInfoDict):
        if len(documentInfoDict) == 0:
            return []
        
        documentInfoDictItems = list(documentInfoDict.items())

        cutoffPoint = 100
        maxCutofPoint = 1600
        lengthneeded = self.numResults
        while True:
            documentswithAll = [[docInfo[0], docInfo[2]] for docInfo in documentInfoDictItems[0][1][:cutoffPoint]]
            
            for stemDocInfo in documentInfoDictItems[1:]:
                documentswithAll = self.intersect(documentswithAll, [[docInfoItem[0], docInfoItem[2]] for docInfoItem in stemDocInfo[1][:cutoffPoint]])
            
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
    
    # intersection of document ids / sum intersecting scores
    # ex: [[id1, score1], [id5, score2]] and [[id5, score3], [id7, score4]] => [[id1, score1], [id5, score2+score3], [id7, score4]]
    def intersect(self, lst1, lst2):
        s1 = set([x[0] for x in lst1])
        s2 = set([x[0] for x in lst2])

        d1 = {x[0]: x[1] for x in lst1}
        d2 = {x[0]: x[1] for x in lst2}

        s = s1.intersection(s2)

        l = []
        for i in s:
            tot = 0
            if i in d1:
                tot += d1[i]
            if i in d2:
                tot += d2[i]
            l.append([i, tot])
        
        # sort intersection results by value
        l.sort(key=lambda x: x[1])

        return l
        
    # Updates score for each document, based on tf-idf weight of query term.
    # documentInfoDictInfo{'stem', [[doc number, [postions], tfidf_score]}    
    #
    def cosineSim(self, query, documentInfoDict, documentswithAll):
        scores = {} # new scores

        query = query.split(" ")
        # iterate through each term in query
        for stem in documentInfoDict:
            documents = documentInfoDict[stem]
            df = len(documents)
            qFreq = self.queryFreq(query, stem)
            for posting in documents:
                doc_id = posting[0]
                tf_idf = posting[2]
                qScore = self.tf_idfScore(df,qFreq)
                # calculate and update total score
                
                if doc_id in scores:
                    scores[doc_id] += qScore * tf_idf
                else:
                    scores[doc_id] = qScore * tf_idf
        
        # factor document size into scores      
        for doc_id, score in scores.items():
            doc_len = max(math.log10(self.docInfoLst[doc_id][2]), 1)
            scores[doc_id] = round(score / doc_len, 3)
        
        #replace old scores with new scores
        for doc in documentswithAll:
            if doc[0] in scores:
                doc[1] = scores[doc[0]]

    def queryFreq(self, query, word):
        count = 0
        for q in query:
            if self.porterStemmer.stem(q) == word:
                count += 1
        return count
    
    # tf-idfscore:
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

    #inverse document frequency score
    # docFreq is the the number of documents that contain term
    def idfScore(self, docFreq):
        return math.log10(self.numDocuments/docFreq)

    # return list of titles and urls given a list of document ids
    def getDocumentsInfo(self, docNums):
        return [[self.docInfoLst[docNum][0], self.docInfoLst[docNum][1]] for docNum in docNums]

    # print list of titles and urls given a list of document ids
    def printDocumentsInfo(self, docNums):
        print("\n".join(self.docInfoLst[docNum][0]+"\n\t"+self.docInfoLst[docNum][1] for docNum in docNums))
    
    # retreive results for the query
    # which calls the ANDBoolean function 
    # -- meaning that every token in the query will be in every returned document
    # modify 
    def getQueryResultsUtil(self, text, usebigram):
        if usebigram:
            documentInfoDict = self.docInfoRetrieve(text, self.tokenizeBigramStop, self.stemBigram, self.bigramIndexFile, self.bigramStemPositions)
        else:
            documentInfoDict = self.docInfoRetrieve(text)
        # get document with tf-idf score
        res = self.ANDBoolean(documentInfoDict)
        # bigram / cosine similarity
        if len(documentInfoDict) > 1:
            if not usebigram:
                self.bigramscoring(res, text)
            self.cosineSim(text, documentInfoDict, res)

        return res
    
    def splitQuery(self, a, n):
        k, m = divmod(len(a), n)
        return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]
    
    def allStopWordQuery(self, ts):
        for t in ts:
            if t not in self.STOPWORDS:
                return False
        return True

    def getQueryResults(self, text):
        # time start
        start_time = datetime.datetime.now()

        res = {}
        div = 1
        ts = text.split()

        # if the query is only stop words, then do not remove any stopwords from the query
        queryISAllStopWords = False
        if self.allStopWordQuery(ts):
            self.stopwords = {}
            queryISAllStopWords = True
        
        # take union of parts of query search results until there are enough results
        # ex: 
        while len(res) < self.numResults and div <= len(ts):
            subres = {}
            subtexts = self.splitQuery(ts, div)
            for t in subtexts:
                # only bigram search if query is all stop words
                r = self.getQueryResultsUtil(" ".join(t), queryISAllStopWords)
                for ri in r:
                    if ri[0] not in subres:
                        subres[ri[0]] = ri[1]
                    else:
                        subres[ri[0]] += ri[1]
            
            # add new results on top of old ones -- do not overwrite
            for k, v in subres.items():
                if k not in res:
                    res[k] = v
            div *= 2
        
        res = list(res.items())

        # reset stopwords if changed
        if queryISAllStopWords:
            self.stopwords = self.STOPWORDS

        # res = self.getQueryResultsUtil(text)

        res = sorted(res, key=lambda x: x[1], reverse=True)[:self.numResults]

        # time end
        end_time = datetime.datetime.now()
        timemilli = (end_time - start_time).total_seconds() * 1000.0

        return res, timemilli

    def printQueryResults(self, text):
        res, timemilli = self.getQueryResults(text)
        print(f"time: {timemilli} milliseconds")
        self.printDocumentsInfo([r[0] for r in res])