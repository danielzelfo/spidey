from Indexer import Indexer
from pathlib import Path

directory = "page_data/data/DEV/"
indexer = None

def run():
    global directory
    indexer = Indexer()
    for filepath in Path(directory).rglob('*.json'):
        print("current file: ", filepath)
        indexer.index(filepath)

if __name__ == "__main__":
    run()