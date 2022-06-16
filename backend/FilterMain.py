import os
from datetime import datetime
from pathlib import Path
from Filter import Filter
import warnings
import glob
import tarfile
import shutil
warnings.filterwarnings("ignore")

#Directory of files
page_data_dir = "page_data/"
input_directory = f"page_data/data/"
input_tar_parts = "page_data/data.tar.gz-parta*"
input_tar = "page_data/data.tar.gz"
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

    print("Extracting page data...")

    # combine part tar files
    os.system(f"cat {input_tar_parts} > {input_tar}")
    
    # extract combined tar file
    data = tarfile.open(input_tar)
    data.extractall(page_data_dir)
    data.close()

    # delete full tar file after extracting
    os.unlink(input_tar)

    print("Running filter...")
    input_files = list(Path(input_directory).rglob('*.json'))
    Filter(input_files, output_directory, run_log).run_filter()

    run_log.write("FILTER RUN ENDED AT: " + str(datetime.now()) + "\n")
    run_log.close()
    
    # delete extracted page data
    try:
        shutil.rmtree(input_directory)
    except OSError as e:
        pass

if __name__ == "__main__":
    run()
