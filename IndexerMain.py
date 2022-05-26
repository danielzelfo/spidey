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
directory = "page_data/filtered_small/"

# Main Program
# Initalizes Indexer, reads and offloads data, merges data into single file when finished.

def build_index(num_documents, index_function):
    with alive_bar(num_documents, force_tty=True) as bar:
        with open("docInfo.txt", "r") as files:
            for fileInfo in files:
                fileInfoArr = json.loads(fileInfo)
                title = fileInfoArr[0]
                importantTagExtentList = fileInfoArr[4]
                filepath = os.path.join(directory, fileInfoArr[2])
                index_function(filepath, title, importantTagExtentList)
                bar()

def run():
    run_log = open("run_log.txt", "a")
    run_log.write("INDEX RUN STARTED AT: " + str(datetime.datetime.now()) + "\n")

    with open("num_documents.txt", "r") as f:
        num_documents = int(f.read().strip())

    indexer = Indexer(num_documents, run_log=run_log)
    
    print("BUILDING INDEX...")
    build_index(num_documents, indexer.index)
    
    # reset indexing variables
    indexer.reset()

    print("BUILDING BIGRAM INDEX...")
    build_index(num_documents, indexer.bigram_index)
    
    stem_counts = indexer.k_way_merge_files()

    indexer.post_index_score(stem_counts)

    run_log.write("INDEX RUN ENDED AT: " + str(datetime.datetime.now()) + "\n")
    run_log.close()

if __name__ == "__main__":
    run()
