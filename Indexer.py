import json
from HTMLParser import HTMLParser

class Indexer:

    def __init__(self, entries_per_offload=200000, run_log=None):
        self.entries_per_offload = entries_per_offload
        self.run_log = run_log

        self.htmlParser = HTMLParser()

        self.current_data = {}
        self.urls = {}

        self.document_count = 0
        self.database_num = 0
        self.num_values = 0
        
    # filepath ex: aiclub_ics_uci_edu/file.json
    # Extracts and tokenizes text from given filepath
    # Stores tokens into dictionary
    # Offloads dictionary once token entires exceeds threshold
    def index(self, filepath):
        self.document_count += 1
        
        # extract data from file
        with open(filepath) as f:
            data = json.load(f)
            content = data["content"]
            encoding = data["encoding"]
            url = data["url"]
    
        self.urls[url] = self.document_count
        
        # safely extract text
        try:
            textContent = self.htmlParser.extract_text(content, encoding, url)
        except Exception as e:
            print(f"Extract text error for {url}: {e}")
            if not self.run_log is None:
                self.run_log.write(f"Extract text error for {url}: {e}\n")
            return
        
        # Get stems & positions dictionary
        stemPositions = self.htmlParser.tokensAndPositionsToStemDict(self.htmlParser.tokenize(textContent))
        
        # Add new token value into current data
        # Offload if number of value exceeds threshold
        for stem, positions in stemPositions.items():
            if not stem in self.current_data:
                self.current_data[stem] = []
                
            self.current_data[stem].append([self.document_count, positions])
            
            self.num_values += 1
            if self.num_values >= self.entries_per_offload:
                self.offload()
                self.num_values = 0
    
    # Saves url hashtable into json file
    def save_urls(self):
        with open("urls.txt", "w") as f:
            for url, idx in self.urls.items():
                f.write(f"{idx}:{url}\n")
    
    # Opens/Create file for offloading tokens
    # write everything in current_data / clear current_data
    def offload(self):
        print(f"OFFLOADING {self.database_num}...")
        with open(f"database_{self.database_num}.txt", "w") as f:
            for token, entries in sorted(self.current_data.items(), key=lambda x: x[0]):
                self.write_to_disk(f, token, entries)
        
        self.current_data = {}
        self.database_num += 1
    
    # writes token and entries into file
    def write_to_disk(self, file, token, entries):
        file.write(f"{token}:")
        for entry in entries:
            entrystr = json.dumps(entry)
            file.write(f"[{len(entrystr)}]{entrystr}")
        
        file.write("\n")
        
    # Merges all database.txt files together into one big database.txt file
    def k_way_merge_files(self):
        # open the merged database file
        outfile = open("database_merged.txt", "w")
        # open the k database files
        infiles = [open(f"database_{k}.txt", "r") for k in range(self.database_num)]

        # read first line of all k database files
        lines = [x for x in [file.readline().strip() for file in infiles] if x]

        # stems are before the colon / lines are everything after the stem
        stems = [line.split(":")[0] for line in lines]
        lines = [line[len(stem)+1:] for line, stem in zip(lines, stems)]

        current_stem = None
        while len(lines) > 0:
            # get minimum stem
            min_idx = stems.index(min(stems))
            # if the minimum stem is not that same as the last one (or the first one) write it
            if current_stem is None or current_stem != stems[min_idx]:
                current_stem = stems[min_idx]
                outfile.write(f"\n{current_stem}:")
            
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
        
        outfile.close()
