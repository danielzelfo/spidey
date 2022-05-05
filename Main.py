from Indexer import Indexer
from pathlib import Path
from alive_progress import alive_bar
import datetime
import warnings
warnings.filterwarnings("ignore")

directory = "page_data/data/DEV/"

#testDirectory = "testing/"

indexer = None

def run():
    
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
    
    print("Merging database files...")
    indexer.k_way_merge_files()
    indexer.save_urls()
    run_log.write("RUN ENDED AT: " + str(datetime.datetime.now()) + "\n")
    run_log.close()

if __name__ == "__main__":
    run()