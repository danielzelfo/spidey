import os
import json
from HTMLParser import HTMLParser

class Indexer:

    def __init__(self, documents_per_file=200):
        self.htmlParser = HTMLParser()

        # Dictionary of stem: [db file num, array index]
        # Note: Since Python 3.6, dictionaries retain their insertion order
        self.stem_position_indices = {}
        # Array of [end of line position, number of entries in current database file]
        self.stem_positions = [[]]
        # Array of cursors for each database file (current number of characters in file)
        self.database_cursors = [0]

        self.max_documents_per_file = documents_per_file

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
    
    def write_entry(self, file, entry, length):
        # write [length]{data}
        self.write_to_f(file, f"[{length}]")
        self.write_to_f(file, entry)
    
    def write_to_disk(self, stem, document, documentposition, terms, frequency):
        entry = json.dumps([document, documentposition, terms, frequency])
        length = len(entry)

        # length of of entry [length]{data}
        charactersAdded = len(str(length)) + 2 + length

        # check if the stem has never been seen before
        # get index of stem position
        if not stem in self.stem_position_indices:
            current_db_page = 0
            stemArrIdx = len(self.stem_positions[current_db_page])
            self.stem_position_indices[stem] = [current_db_page, stemArrIdx]
            self.stem_positions[current_db_page].append([self.database_cursors[current_db_page], 0])
        else:
            current_db_page = self.stem_position_indices[stem][0]
            stemArrIdx = self.stem_position_indices[stem][1]
        
        # check if the number of entries for the current stem exceeded the max for the current database file
        if self.stem_positions[current_db_page][stemArrIdx][1] >= self.max_documents_per_file:
            current_db_page += 1

            # add to database cursor if document number has never been reached before
            if len(self.database_cursors) <= current_db_page:
                self.database_cursors.append(0)

            if len(self.stem_positions) <= current_db_page:
                self.stem_positions.append([])
            
            stemArrIdx = len(self.stem_positions[current_db_page])
            
            if len(self.stem_positions[current_db_page]) <= stemArrIdx:
                self.stem_positions[current_db_page].append([self.database_cursors[current_db_page], 0])


            # update stem position
            self.stem_position_indices[stem][0] = current_db_page
            self.stem_position_indices[stem][1] = stemArrIdx
            self.stem_positions[current_db_page][stemArrIdx][0] = self.database_cursors[current_db_page]
            self.stem_positions[current_db_page][stemArrIdx][1] = 0

        # check if the current stem has no entries in the current database file
        if self.stem_positions[current_db_page][stemArrIdx][1] == 0:
            # append to end of file
            file = open(f"database_{current_db_page}.txt", "a")

            # write stem
            self.write_to_f(file, f"\n{stem}:")
            charactersAdded += 1 + len(stem) + 1

            # write entry
            self.write_entry(file, entry, length)
        else:
            # if stem exists then seek to end of stem line
            file = open(f"database_{current_db_page}.txt", "r+")
            file.seek(self.stem_positions[current_db_page][stemArrIdx][0])


            # copy all data after current position to temporary file
            with open("temp_file.txt", "w") as temp:
                for line in file:
                    temp.write(line)

            # go back to end of line for stem
            file.seek(self.stem_positions[current_db_page][stemArrIdx][0])
            
            # write entry
            self.write_entry(file, entry, length)

            # re-write overwritten data
            with open("temp_file.txt", "r") as temp:
                for line in temp:
                    file.write(line)

        file.close()

        if os.path.isfile("temp_file.txt"):
            os.unlink("temp_file.txt")

        # update end of line for stem
        self.stem_positions[current_db_page][stemArrIdx][0] += charactersAdded
        # increment number of entries for stem
        self.stem_positions[current_db_page][stemArrIdx][1] += 1

        # update character positions for all stems after (this does nothing if stem is new)
        for i in range(stemArrIdx+1, len(self.stem_positions[current_db_page])):
            self.stem_positions[current_db_page][i][0] += charactersAdded

        # update character position for current database file
        self.database_cursors[current_db_page] += charactersAdded