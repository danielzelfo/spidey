import os
import json
from HTMLParser import HTMLParser

class Indexer:

    def __init__(self, documents_per_offload=2000):
        self.htmlParser = HTMLParser()

        self.current_data = {}

        self.document_per_offload = documents_per_offload
        self.document_count = 0
        self.database_num = 0
    
    # filepath ex: aiclub_ics_uci_edu/file.json
    def index(self, filepath):
        self.document_count += 1

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

        for i, (token, freq) in enumerate(tokenFreq.items()):
            if not token in self.current_data:
                self.current_data[token] = []
            self.current_data[token].append([url, 0, 0, freq])
        
        if self.document_count % self.document_per_offload == 0:
            self.offload()
    
    def offload(self):
        print("OFFLOADING...")
        with open(f"database_{self.database_num}.txt", "w") as f:
            for token, entries in sorted(self.current_data.items()):
                self.write_to_disk(f, token, entries)
        
        self.current_data = {}
        self.database_num += 1
    
    def write_to_disk(self, file, token, entries):
        entries_parsed = f"{token}:"
        for entry in entries:
            entrystr = json.dumps(entry)
            entries_parsed += f"[{len(entrystr)}]{entrystr}\n"
        
            file.write(entries_parsed)
    
    def k_way_merge_files(self):
        outfile = open("database_merged.txt", "w")
        infiles = [open(f"database_{i}.txt", "r") for i in range(self.database_num+1)]
        lines = [x for x in [file.readline().strip() for file in infiles] if x]
        stems = [line.split(":")[0] for line in lines]
        lines = [line[len(stem)+1:] for line, stem in zip(lines, stems)]

        current_stem = None
        while len(lines) > 0:
            min_idx = stems.index(min(stems))
            if current_stem is None or current_stem != stems[min_idx]:
                current_stem = stems[min_idx]
                outfile.write(f"\n{current_stem}:")
            
            outfile.write(lines[min_idx])
            
            lines[min_idx] = infiles[min_idx].readline().strip()
            if not lines[min_idx]:
                del lines[min_idx]
                del stems[min_idx]
                infiles[min_idx].close()
                del infiles[min_idx]
            else:
                stems[min_idx] = lines[min_idx].split(":")[0]
                lines[min_idx] = lines[min_idx][len(stems[min_idx])+1:]
        
        outfile.close()
