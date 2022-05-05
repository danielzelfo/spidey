import os
import json
from HTMLParser import HTMLParser

class Indexer:

    def __init__(self):
        # Dictionary of stem: [index, start of line, end of line]
        # Note: Since Python 3.6, dictionaries retain their insertion order
        self.stem_position_indices = {}
        self.stem_positions = []
        self.database_cursor = 0

        self.htmlParser = HTMLParser()
        pass

    def write_to_f(self, f, strr):
        # print(f"Writing: {strr}")
        f.write(strr)
    
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
            self.write_to_disk(token, url, 0, 0, freq)
        
    
    def write_to_disk(self, stem, document, documentposition, terms, frequency):
        datawriting = json.dumps({
            "document": document,
            "documentposition": documentposition,
            "terms": terms,
            "frequency": frequency
        })
        length = len(datawriting)

        # length of [length]{data}
        charactersAdded = len(str(length)) + 2 + length

        stemArrIdx = 0

        if stem not in self.stem_position_indices:
            stemArrIdx = len(self.stem_position_indices)
            self.stem_position_indices[stem] = stemArrIdx
            self.stem_positions.append([self.database_cursor, self.database_cursor])
            
            # if stem does not exist, then append to end of line
            file = open("database.txt", "a")

            # write stem
            self.write_to_f(file, f"\n{stem}:")
            charactersAdded += 1 + len(stem) + 1
        else:            
            # seek to end of line for stem
            stemArrIdx = self.stem_position_indices[stem]

            # if stem exists then seek to end of stem line
            file = open("database.txt", "r+")
            
            # go to end of line for stem
            file.seek(self.stem_positions[stemArrIdx][1])

            # copy all data after current position to temporary file
            with open("temp_file.txt", "w") as temp:
                for line in file:
                    temp.write(line)

            # move down data so it is not overwritten
            file.seek(self.stem_positions[stemArrIdx][1] + charactersAdded)
            with open("temp_file.txt", "r") as temp:
                for line in temp:
                    file.write(line)

            # go back to end of line for stem
            file.seek(self.stem_positions[stemArrIdx][1])
        
        # write [length]{data}
        self.write_to_f(file, f"[{length}]")
        self.write_to_f(file, datawriting)

        # update end of line for stem
        self.stem_positions[stemArrIdx][1] += charactersAdded

        # update character positions for all stems after (this does nothing if stem is new)
        for i in range(stemArrIdx+1, len(self.stem_positions)):
            self.stem_positions[i][0] += charactersAdded
            self.stem_positions[i][1] += charactersAdded

        self.database_cursor += charactersAdded

        file.close()

        if os.path.isfile("temp_file.txt"):
            os.unlink("temp_file.txt")