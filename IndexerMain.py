from Indexer import Indexer
from pathlib import Path
from alive_progress import alive_bar
import datetime
import glob
import os
import warnings
warnings.filterwarnings("ignore")

#Directory of files
directory = "page_data/data/DEV/"

# Main Program
# Initalizes Indexer, reads and offloads data, merges data into single file when finished.
def run():
    # delete index file from previous run
    if os.path.isfile("index.txt"):
        os.unlink("index.txt")
    
    run_log = open("run_log.txt", "a")
    run_log.write("RUN STARTED AT: " + str(datetime.datetime.now()) + "\n")

    indexer = Indexer(run_log=run_log)
    files = list(Path(directory).rglob('*.json'))

    with alive_bar(len(files), force_tty=True) as bar:
        for filepath in files:
            # print("current file: ", filepath)
            indexer.index(filepath)
            bar()
        indexer.offload()
    
    print("Merging index files...")
    indexer.k_way_merge_files()
    # delete partial index files
    for file in glob.glob('index_*.txt'):
        os.unlink(file)

    print("Saving url ids")
    indexer.save_urls()

    run_log.write("RUN ENDED AT: " + str(datetime.datetime.now()) + "\n")
    run_log.close()

if __name__ == "__main__":
    run()
