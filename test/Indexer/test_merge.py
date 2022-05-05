import os
import shutil

os.chdir(os.path.dirname(os.path.realpath(__file__)))

shutil.copyfile("../../Indexer.py", "Indexer.py")
shutil.copyfile("../../HTMLParser.py", "HTMLParser.py")

from Indexer import Indexer

indexer = Indexer()
indexer.database_num = 2
indexer.k_way_merge_files()

os.unlink("Indexer.py")
os.unlink("HTMLParser.py") 