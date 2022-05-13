from nltk.stem import PorterStemmer
import json

class Query:
    def __init__(self):
        self.indexStemPositions = { }
        self.indexFile = open("index.txt", "r")
        self.porterStemmer = PorterStemmer()
        self.docInfoLst = []
        with open("docInfo.txt", "r") as f:
            for line in f:
                docInfo = json.loads(line.strip())
                self.docInfoLst.append(docInfo[:2])#only save title and url

        self.initializeIndexStemPositions()

        
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
        splitText = text.strip().split(" ")

        documentInfoDict = {}
        
        for word in splitText:
            stem = self.porterStemmer.stem(word)
            documentInfoDict[stem] = self.stemDocInfoRetrieve(stem)
        
        return documentInfoDict
            
    def ANDboolean(self, documentInfoDict):
        documentInfoDictItems = list(documentInfoDict.items())

        documentswithAll = set([docInfo[0] for docInfo in documentInfoDictItems[0][1]])
        for stemDocInfo in documentInfoDictItems[1:]:
            documentswithAll = documentswithAll.intersection(docInfoItem[0] for docInfoItem in stemDocInfo[1])
        return documentswithAll

    # def ranking(self, documentSet):
        

    def printDocumentsInfo(self, docNums):
        print("\n".join(self.docInfoLst[docNum][0]+"\n\t"+self.docInfoLst[docNum][1] for docNum in docNums))
    
    def printQueryResults(self, text):
        self.printDocumentsInfo(list(self.ANDboolean(self.docInfoRetrieve(text)))[:5])