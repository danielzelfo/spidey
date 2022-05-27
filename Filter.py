import json
import os
from alive_progress import alive_bar
from urllib.parse import urldefrag
from HTMLParser import HTMLParser

class Filter:
    def __init__(self, files, textContentSavePath, run_log):
        self.files = files
        self.textContentSavePath = textContentSavePath
        self.run_log = run_log
        self.htmlParser = HTMLParser()
        self.countSuccessFul = 0
        self.encountered_urls = set()
        self.footprints = []
        self.importantTags = ["b", "strong", "h1", "h2", "h3"]
        self.duplicateThreshold = 0.97

    def get_footprint(self, dict1):
        keys = list(dict1.keys())
        vector = [0] * 64
        for i in keys:
            key = i
            i = format(hash(i), '0>64b')[-64:]                      #hash tokens into 64 bit
            for j in range(len(vector)):
                if i[j] == "1":
                    vector[j] = vector[j] + (dict1[key] * int(i[j]))    #if index of key is 1, multiply token freq by 1
                else:
                    vector[j] = vector[j] + (dict1[key] * -1)           #if index of key is 1, multiply token freq by -1
        for i in range(len(vector)):
            if vector[i] >= 1:
                vector[i] = 1                                       #if index is positive, set vector[index]=1
            else:
                vector[i] = 0                                       #if index is negative, set vector[index]=0
        return "".join([str(z) for z in vector])

    def filter_file(self, filepath, docInfoFile):
        with open(filepath) as f:
            data = json.load(f)
            content = data["content"]
            encoding = data["encoding"]
            url = data["url"]
        
        url = urldefrag(url)[0]
        if url in self.encountered_urls:
            return

        # safely extract text
        try:
            
            importantTagsExtentLists = {}
            title, textContentElems = self.htmlParser.extract_info(content, encoding, url)

            filename = os.path.split(filepath)[-1]
            saveFilePath = os.path.join(self.textContentSavePath, filename)
            
            freqDict = {}
            tokenLength = 0
            fileLength = 0
            with open(saveFilePath, "w") as f:
                for textElem in textContentElems:
                    
                    elemText = ""
                    for to in self.htmlParser.tokenize(textElem[1]):
                        tokenLength += 1
                        token = to[0]
                        if not token in freqDict:
                            freqDict[token] = 1
                        else:
                            freqDict[token] += 1
                        
                        elemText += token + " "
                    
                    for tag in self.importantTags:
                        if textElem[0] == tag:
                            if not tag in importantTagsExtentLists:
                                importantTagsExtentLists[tag] = [[fileLength, fileLength + len(elemText)-1]]
                            else:
                                importantTagsExtentLists[tag].append([fileLength, fileLength + len(elemText)-1])
                            break
                    
                    fileLength += len(elemText)
                    f.write(elemText)
                
            if tokenLength == 0:
                return
            
            footprint = [self.get_footprint(freqDict), tokenLength]
            # loop through all other footprints and compare
            # if similar then stop here
            for i, comparefootprint in enumerate(self.footprints):
                counter = 0
                for j in range(64):
                    if footprint[0][j] == comparefootprint[0][j]: 
                        counter += 1
                similarity = counter/64
                if similarity > self.duplicateThreshold and min(comparefootprint[1], footprint[1])/max(comparefootprint[1], footprint[1]) > self.duplicateThreshold:
                    return
            
            self.footprints.append(footprint)
            # save document Info
            docInfoFile.write(f"{json.dumps([title, url, filename, tokenLength, importantTagsExtentLists], separators=(',', ':'))}\n")
        
            self.countSuccessFul += 1

            self.encountered_urls.add(url)

        except Exception as e:
            print(f"Extract text error for {url}: {e}")
            if not self.run_log is None:
                self.run_log.write(f"Extract text error for {url}: {e}\n")
    
    def run_filter(self):
        with open("docInfo.txt", "w") as docInfoFile:
            with alive_bar(len(self.files)) as bar:
                for filepath in self.files:
                    self.filter_file(filepath, docInfoFile)
                    bar()
        with open("num_documents.txt", "w") as f:
            f.write(str(self.countSuccessFul))
        