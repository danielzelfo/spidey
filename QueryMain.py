import sys
from Query import Query

if __name__ == "__main__":
    query = Query()
    
    while True:
        request = input("Enter Search Query: ")
        if request == "Done":
            break
    
        query.printQueryResults(request)
    
    