import json
import math
import os
from alive_progress import alive_bar
from HTMLParser import HTMLParser
from Ranking import Ranking
import time


# Class to build and maintain indexer to store stems and their postings of documents
class Indexer:
    def __init__(self, numDocuments, entries_per_offload=1000000, run_log=None):
        self.entries_per_offload = entries_per_offload
        self.run_log = run_log

        self.htmlParser = HTMLParser()

        self.current_data = {}

        self.document_count = 0
        self.index_num = {}
        self.num_values = 0

        self.importantTagExtentLists = []

        self.BIGRAM_INDEX_PATH = "bigram_index"
        self.INDEX_PATH = "index"

        self.ALL_INDEX_PATHS = [self.INDEX_PATH, self.BIGRAM_INDEX_PATH]

        for indexfile in self.ALL_INDEX_PATHS:
            # delete index file from previous run
            if os.path.isfile(f"{indexfile}.txt"):
                os.unlink(f"{indexfile}.txt")

        #Total number of documents
        self.numDocuments = numDocuments
    
    def reset(self):
        self.document_count = 0
        self.num_values = 0

    def processStemPositions(self, stemPositions, index_path):
        for stem, positions in stemPositions.items():
            if not stem in self.current_data:
                self.current_data[stem] = []
            
            # negative position to denote a title
            self.current_data[stem].append([self.document_count, positions])

            self.num_values += 1
            if self.num_values >= self.entries_per_offload:
                self.offload(index_path)
                self.num_values = 0
    
    def tokenizeProcTextContent(self, text):
        # tokens from text content file
        pos = 0
        for token in text.split():
            yield [token, pos]
            pos += len(token) + 1

    # filepath ex: direc/file.json
    # Stores tokens into dictionary
    # Offloads dictionary once token entires exceeds threshold
    def index(self, filepath, title, importantTagExtentList, numTokens):
        # extract data from file
        if not os.path.isfile(filepath):
            print("WARNING: called index with file that doesn't exist.")
            return
        
        with open(filepath) as f:
            textContent = f.read()
        
        #title stems and positions dictionary
        titleStemPositions = self.htmlParser.tokensAndPositionsToStemDict(self.htmlParser.tokenize(title))
        stemPositions = {}
        for stem, positions in titleStemPositions.items():
            stemPositions[stem] = [-1*(pos+1) for pos in positions]
        
        # tokens from text content file
        tokens = self.tokenizeProcTextContent(textContent)
        
        # Get stems & positions dictionary
        stemPositionsText = self.htmlParser.tokensAndPositionsToStemDict(tokens)
        for stem, positions in stemPositionsText.items():
            if stem in stemPositions:
                stemPositions[stem] += positions
            else:
                stemPositions[stem] = positions
        
        # Add new token value into current data
        # Offload if number of value exceeds threshold
        self.processStemPositions(stemPositions, self.INDEX_PATH)
        
        self.document_count += 1

        self.importantTagExtentLists.append(importantTagExtentList)

        if self.document_count == self.numDocuments:
            self.offload(self.INDEX_PATH)
            self.reset()

    def bigram_index(self, filepath, title, importantTagExtentList, numTokens):
        # not saving importantTagExtentList, numTokens because it is saved in self.index(...)
        if not os.path.isfile(filepath):
            print("WARNING: called bigram_index with file that doesn't exist.")
            return

        # extract data from file
        with open(filepath) as f:
            textContent = f.read()
        
        #title stems and positions dictionary
        titleStemPositions = self.htmlParser.tokensAndPositionsToStemDict(self.htmlParser.bigram_tokenize(text=title))
        stemPositions = {}
        for stem, positions in titleStemPositions.items():
            stemPositions[stem] = [-1*(pos+1) for pos in positions]
        
        # tokens from text content file
        tokens = self.tokenizeProcTextContent(textContent)
        tokens = self.htmlParser.bigram_tokenize(self, tokens_iter=tokens)
        
        # Get stems & positions dictionary
        stemPositionsText = self.htmlParser.tokensAndPositionsToStemDict(tokens)
        for stem, positions in stemPositionsText.items():
            if stem in stemPositions:
                stemPositions[stem] += positions
            else:
                stemPositions[stem] = positions
        
        # Add new token value into current data
        # Offload if number of value exceeds threshold
        self.processStemPositions(stemPositions, self.BIGRAM_INDEX_PATH)
        
        self.document_count += 1

        if self.document_count == self.numDocuments:
            self.offload(self.BIGRAM_INDEX_PATH)
            self.reset()
    
    def post_index_score(self, num_stems):
        for index_path in self.ALL_INDEX_PATHS:
            if not index_path in self.index_num:
                continue
            print(f"Scoring/sorting {index_path}...")
            os.rename(f"{index_path}.txt", f"{index_path}.old.txt")
            with open(f"{index_path}.old.txt", "r") as infile:
                infile.readline() # skip first new line
                with open(f"{index_path}.txt", "w") as outfile:
                    with alive_bar(num_stems[index_path], force_tty=True) as bar:
                        for line in infile:
                            # old stemInfo{'stem', [[doc number, [postions]]} ->
                            # new stemInfo{'stem', [[doc number, [postions], tfidf_score]}
                            stem, stemInfo = self.parseLine(line)
                            #TFIDF SCORE
                            scores = self.calculateTfIdfScore(stemInfo)
                            #APPEND TO docInfo 
                            for posting in stemInfo:
                                doc_number = posting[0]
                                doc_score = scores[doc_number]

                                doc_score = round(doc_score, 4)

                                posting.append(doc_score)
                            # sort by td-idf score
                            if index_path != "bigram_index":
                                stemInfo.sort(key=lambda x: x[2], reverse=True)

                            #rewrite
                            self.write_to_disk(outfile, stem, stemInfo)
                            bar()
            os.unlink(f"{index_path}.old.txt")
    
    def calculateTfIdfScore(self, documentInfo):
        
        # for each word in documentInfo
        # for each document in word, check if document is in word posting
        # count the frequency, store into a dictionary
        # new stemInfo [[doc number, [postions,pos2,pos3], tfidf_score], [doc number, [postions,pos2,pos3], tfidf_score]]
        # documents = documentInfo[1]
        
        documentRank = {}

        documentFrequency = len(documentInfo) # Number of documents per term
        
        for doc in documentInfo:
            termFreq = Ranking.positionsToRank(doc[1], self.importantTagExtentLists[doc[0]])
            #count frequency (calculate score with tf-idf)
            score =  self.tf_idfScore(documentFrequency, termFreq)
            
            if doc[0] in documentRank:
                documentRank[doc[0]] = documentRank[doc[0]] + score
            else:
                documentRank[doc[0]] = score

        documentRank = dict(sorted(documentRank.items(), key = lambda x: x[1], reverse=True))
        
        return documentRank
        
    # tf-idf score:
    # w(t,d) = (1+log(term freq per document)) * log(N/doc freq)
    def tf_idfScore(self, docFreq, termFreq):
        tf = self.tfScore(termFreq)

        idf = self.idfScore(docFreq)

        tf_idf = tf * idf

        # print(f"tf{tf}, idf{idf}, tf_idf, {tf_idf}")

        return tf_idf

    # Function to calculate tf Score
    def tfScore(self, termFreq):
        weightScore = 0
        if termFreq > 0:
            weightScore = 1 + math.log10(termFreq)

        return weightScore

    # docFreq is the the number of documents that contain term
    def idfScore(self, docFreq):
        return math.log10(self.numDocuments/docFreq)
    
    # Opens/Create file for offloading tokens
    # write everything in current_data / clear current_data
    def offload(self, index_path):
        if not index_path in self.index_num:
            self.index_num[index_path] = 0
        print(f"OFFLOADING {self.index_num[index_path]}...")
        with open(f"{index_path}_{self.index_num[index_path]}.txt", "w") as f:
            for token, entries in sorted(self.current_data.items(), key=lambda x: x[0]):
                self.write_to_disk(f, token, entries)
        
        self.current_data = {}
        self.index_num[index_path] += 1
    
    # writes token and entries into file
    def write_to_disk(self, file, token, entries):
        file.write(f"{token}:")
        for entry in entries:
            entrystr = json.dumps(entry, separators=(',', ':'))
            file.write(f"[{len(entrystr)}]{entrystr}")
        
        file.write("\n")
        
    # Merges all index_*.txt files together into one big index.txt file
    def k_way_merge_files(self):
        stem_counts = {}
        for index_path in self.ALL_INDEX_PATHS:
            if not index_path in self.index_num:
                continue
            print(f"Merging {index_path}...")
            # open the merged index file
            outfile = open(f"{index_path}.txt", "w")
            # open the k index files
            infile_paths = [f"{index_path}_{k}.txt" for k in range(self.index_num[index_path])]
            infiles = [open(p, "r") for p in infile_paths]

            # read first line of all k index files
            lines = [x for x in [file.readline().strip() for file in infiles] if x]

            # stems are before the colon / lines are everything after the stem
            stems = [line.split(":")[0] for line in lines]
            lines = [line[len(stem)+1:] for line, stem in zip(lines, stems)]

            current_stem = None
            stem_count = 0
            while len(lines) > 0:
                # get minimum stem
                min_idx = stems.index(min(stems))
                # if the minimum stem is not that same as the last one (or the first one) write it
                if current_stem is None or current_stem != stems[min_idx]:
                    current_stem = stems[min_idx]
                    outfile.write(f"\n{current_stem}:")
                    stem_count += 1
                
                # write the line
                outfile.write(lines[min_idx])
                
                # read next line of file with minimum line
                lines[min_idx] = infiles[min_idx].readline().strip()

                # delete the file / line if EOF is reached
                if not lines[min_idx]:
                    del lines[min_idx]
                    del stems[min_idx]
                    infiles[min_idx].close()
                    del infiles[min_idx]
                
                # separate stem and line
                else:
                    stems[min_idx] = lines[min_idx].split(":")[0]
                    lines[min_idx] = lines[min_idx][len(stems[min_idx])+1:]
            
            stem_counts[index_path] = stem_count

            outfile.close()

            for file in infile_paths:
                os.unlink(file)
            
            print(f"Done merging {index_path}.")

        return stem_counts

    # Function to parse a line in index, returning stem and postings
    def parseLine(self, line):
        documentsInfo = []

        line = line.strip()
        stem = line.split(":")[0]
        line = line[len(stem)+1:]

        # Read [length to read]{doc1 json}[length to read]{doc2 json}
        curidx = 0
        while curidx < len(line):
            jsonlenstr = ""
            for char in line[curidx+1:]:
                if char == "]":
                    break              
                jsonlenstr += char
            jsonlen = int(jsonlenstr)
            documentsInfo.append(json.loads(line[curidx + len(jsonlenstr) + 2 : curidx + len(jsonlenstr) + 2 + jsonlen]))
            curidx += len(jsonlenstr) + 2 + jsonlen

        return stem, documentsInfo