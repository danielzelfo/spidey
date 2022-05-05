
import os
import shutil

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if os.path.exists("./database.txt"):
    os.unlink("./database.txt")

shutil.copyfile("../../Indexer.py", "./Indexer.py")
shutil.copyfile("../../HTMLParser.py", "./HTMLParser.py")


from Indexer import Indexer

indexer = Indexer()
indexer.write_to_disk("key0", "test1", "test1", "test1", "test1")
indexer.write_to_disk("key0", "test2", "test2", "test2", "test2")

indexer.write_to_disk("key1", "test1", "test1", "test1", "test1")
indexer.write_to_disk("key1", "test2", "test2", "test2", "test2")
indexer.write_to_disk("key1", "test3", "test3", "test3", "test3")

indexer.write_to_disk("key2", "test1", "test1", "test1", "test1")
indexer.write_to_disk("key2", "test2", "test2", "test2", "test2")
indexer.write_to_disk("key2", "test3", "test3", "test3", "test3")
indexer.write_to_disk("key2", "test4", "test4", "test4", "test4")

indexer.write_to_disk("key3", "test1", "test1", "test1", "test1")
indexer.write_to_disk("key3", "test2", "test2", "test2", "test2")
indexer.write_to_disk("key3", "test3", "test3", "test3", "test3")
indexer.write_to_disk("key3", "test4", "test4", "test4", "test4")
indexer.write_to_disk("key3", "test5", "test5", "test5", "test5")





indexer.write_to_disk("key0", "2_test1", "2_test1", "2_test1", "2_test1")
indexer.write_to_disk("key0", "2_test2", "2_test2", "2_test2", "2_test2")
indexer.write_to_disk("key0", "2_test3", "2_test3", "2_test3", "2_test3")
indexer.write_to_disk("key0", "2_test4", "2_test4", "2_test4", "2_test4")
indexer.write_to_disk("key0", "2_test5", "2_test5", "2_test5", "2_test5")

indexer.write_to_disk("key1", "2_test1", "2_test1", "2_test1", "2_test1")
indexer.write_to_disk("key1", "2_test2", "2_test2", "2_test2", "2_test2")
indexer.write_to_disk("key1", "2_test3", "2_test3", "2_test3", "2_test3")
indexer.write_to_disk("key1", "2_test4", "2_test4", "2_test4", "2_test4")

indexer.write_to_disk("key2", "2_test1", "2_test1", "2_test1", "2_test1")
indexer.write_to_disk("key2", "2_test2", "2_test2", "2_test2", "2_test2")
indexer.write_to_disk("key2", "2_test3", "2_test3", "2_test3", "2_test3")

indexer.write_to_disk("key3", "2_test1", "2_test1", "2_test1", "2_test1")
indexer.write_to_disk("key3", "2_test2", "2_test2", "2_test2", "2_test2")




indexer.write_to_disk("key0", "3_test1", "3_test1", "3_test1", "3_test1")
indexer.write_to_disk("key0", "3_test2", "3_test2", "3_test2", "3_test2")

indexer.write_to_disk("key1", "3_test1", "3_test1", "3_test1", "3_test1")
indexer.write_to_disk("key1", "3_test2", "3_test2", "3_test2", "3_test2")
indexer.write_to_disk("key1", "3_test3", "3_test3", "3_test3", "3_test3")

indexer.write_to_disk("key2", "3_test1", "3_test1", "3_test1", "3_test1")
indexer.write_to_disk("key2", "3_test2", "3_test2", "3_test2", "3_test2")
indexer.write_to_disk("key2", "3_test3", "3_test3", "3_test3", "3_test3")
indexer.write_to_disk("key2", "3_test4", "3_test4", "3_test4", "3_test4")

indexer.write_to_disk("key3", "3_test1", "3_test1", "3_test1", "3_test1")
indexer.write_to_disk("key3", "3_test2", "3_test2", "3_test2", "3_test2")
indexer.write_to_disk("key3", "3_test3", "3_test3", "3_test3", "3_test3")
indexer.write_to_disk("key3", "3_test4", "3_test4", "3_test4", "3_test4")
indexer.write_to_disk("key3", "3_test5", "3_test5", "3_test5", "3_test5")






indexer.write_to_disk("key0", "4_test1", "4_test1", "4_test1", "4_test1")
indexer.write_to_disk("key0", "4_test2", "4_test2", "4_test2", "4_test2")
indexer.write_to_disk("key0", "4_test3", "4_test3", "4_test3", "4_test3")
indexer.write_to_disk("key0", "4_test4", "4_test4", "4_test4", "4_test4")
indexer.write_to_disk("key0", "4_test5", "4_test5", "4_test5", "4_test5")

indexer.write_to_disk("key1", "4_test1", "4_test1", "4_test1", "4_test1")
indexer.write_to_disk("key1", "4_test2", "4_test2", "4_test2", "4_test2")
indexer.write_to_disk("key1", "4_test3", "4_test3", "4_test3", "4_test3")
indexer.write_to_disk("key1", "4_test4", "4_test4", "4_test4", "4_test4")

indexer.write_to_disk("key2", "4_test1", "4_test1", "4_test1", "4_test1")
indexer.write_to_disk("key2", "4_test2", "4_test2", "4_test2", "4_test2")
indexer.write_to_disk("key2", "4_test3", "4_test3", "4_test3", "4_test3")

indexer.write_to_disk("key3", "4_test1", "4_test1", "4_test1", "4_test1")
indexer.write_to_disk("key3", "4_test2", "4_test2", "4_test2", "4_test2")


os.unlink("./Indexer.py")
os.unlink("./HTMLParser.py")