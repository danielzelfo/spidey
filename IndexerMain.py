from Indexer import Indexer
from pathlib import Path
from alive_progress import alive_bar
import datetime
import glob
import os
import warnings
import json
warnings.filterwarnings("ignore")

#Directory of files
directory = "page_data/filtered_data/"

# Main Program
# Initalizes Indexer, reads and offloads data, merges data into single file when finished.
def run():
    # delete index file from previous run
    if os.path.isfile("index.txt"):
        os.unlink("index.txt")
    
    run_log = open("run_log.txt", "a")
    run_log.write("INDEX RUN STARTED AT: " + str(datetime.datetime.now()) + "\n")

    indexer = Indexer(run_log=run_log)

    with open("num_documents.txt", "r") as f:
        num_documents = int(f.read().strip())
    
    with alive_bar(num_documents, force_tty=True) as bar:
        with open("docInfo.txt", "r") as files:
            for fileInfo in files:
                fileInfoArr = json.loads(fileInfo)
                title = fileInfoArr[0]
                filepath = os.path.join(directory, fileInfoArr[2])
                indexer.index(filepath, title)
                bar()
        indexer.offload()
    
    print("Merging index files...")
    stem_count = indexer.k_way_merge_files()

    print("Scorign and sorting index file...")
    indexer.post_index_score(stem_count)

    # delete partial index files
    for file in glob.glob('index_*.txt'):
        os.unlink(file)


    run_log.write("INDEX RUN ENDED AT: " + str(datetime.datetime.now()) + "\n")
    run_log.close()

if __name__ == "__main__":
    run()
