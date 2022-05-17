import json
import os
from HTMLParser import HTMLParser
from alive_progress import alive_bar
from urllib.parse import urldefrag

class Filter:
    def __init__(self, files, textContentSavePath, run_log):
        self.files = files
        self.textContentSavePath = textContentSavePath
        self.run_log = run_log
        self.htmlParser = HTMLParser()
        self.countSuccessFul = 0
        self.encountered_urls = set()

    def computeWordFrequencies(self, alist):
        adict = dict()
        for i in alist:
            if i not in adict.keys():
                adict[i] = 1
            elif i in adict.keys():
                adict[i] = adict[i] + 1
        return adict

    def get_footprint(self, lst):
        dict1 = self.computeWordFrequencies(lst)
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
        return ("".join([str(z) for z in vector]), len(lst))

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
            title, textContent = self.htmlParser.extract_info(content, encoding, url)
            # replace many whitespace with only 1 space

            # save text content to disk
            filename = os.path.split(filepath)[-1]
            saveFilePath = os.path.join(self.textContentSavePath, filename)
            
            tokens = [x[0] for x in self.htmlParser.tokenize(textContent)]

            with open(saveFilePath, "w") as f:
                f.write(" ".join(tokens))
            
            footprint = self.get_footprint(tokens)
            # save document Info
            docInfoFile.write(f"{json.dumps([title, url, filename, footprint])}\n")

            self.countSuccessFul += 1

            self.encountered_urls.add(url)

        except Exception as e:
            print(f"Extract text error for {url}: {e}")
            if not self.run_log is None:
                self.run_log.write(f"Extract text error for {url}: {e}\n")
    
    def run_filter(self):
        with open("docInfo.txt", "w") as docInfoFile:
            with alive_bar(len(self.files), force_tty=True) as bar:
                for filepath in self.files:
                    self.filter_file(filepath, docInfoFile)
                    bar()
        with open("num_documents.txt", "w") as f:
            f.write(str(self.countSuccessFul))
        