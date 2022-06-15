import os
from datetime import datetime
from pathlib import Path
from Filter import Filter
import warnings
import glob
warnings.filterwarnings("ignore")

#Directory of files
input_directory = "page_data/data/"
output_directory = "page_data/filtered_data/"
if not os.path.isdir(output_directory):
    os.mkdir(output_directory)

# Main Program
# Initalizes Indexer, reads and offloads data, merges data into single file when finished.
def run():
    # delete index file from previous run
    for file in glob.glob(os.path.join(output_directory, '*')):
        os.unlink(file)
    
    run_log = open("run_log.txt", "a")
    run_log.write("RUN FILTER AT: " + str(datetime.now()) + "\n")

    input_files = list(Path(input_directory).rglob('*.json'))
    Filter(input_files, output_directory, run_log).run_filter()

    run_log.write("FILTER RUN ENDED AT: " + str(datetime.now()) + "\n")
    run_log.close()

if __name__ == "__main__":
    run()
