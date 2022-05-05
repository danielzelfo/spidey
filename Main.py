from Indexer import Indexer
from pathlib import Path
from alive_progress import alive_bar

directory = "page_data/data/DEV/"
indexer = None

def run():
    global directory
    indexer = Indexer()
    files = list(Path(directory).rglob('*.json'))
    with alive_bar(len(files)) as bar:
        for filepath in files:
            print("current file: ", filepath)
            indexer.index(filepath)
            bar()
        indexer.offload()
    print("Merging database files...")
    indexer.k_way_merge_files()

if __name__ == "__main__":
    run()