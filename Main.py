from Indexer import Indexer
from pathlib import Path
from alive_progress import alive_bar
import datetime
import warnings
warnings.filterwarnings("ignore")

directory = "page_data/data/DEV/"
indexer = None

def run():
    error_out = open("error_log.txt", "a")
    error_out.write("RUN STARTED AT: " + str(datetime.datetime.now()) + "\n")

    indexer = Indexer(error_out=error_out)
    files = list(Path(directory).rglob('*.json'))
    with alive_bar(len(files), force_tty=True) as bar:
        for filepath in files:
            # print("current file: ", filepath)
            indexer.index(filepath)
            bar()
        indexer.offload()
    
    print("Merging database files...")
    indexer.k_way_merge_files()
    
    error_out.write("RUN ENDED AT: " + str(datetime.datetime.now()) + "\n")
    error_out.close()

if __name__ == "__main__":
    run()