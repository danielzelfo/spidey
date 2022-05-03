class Indexer:
    def __init__(self):
        self.alpha_position_index = {}
        pass
    
    def index(self, filepath):
        # parse
        # stem
        # ...
        # write to disk
        pass
    
    def write_to_disk(self, stem, document, documentposition, terms, frequency):
        # open the disk file
        # check if stem was indexed before
        # if it is
        #     append to end of line ", {document, documentposition, terms, frequency}"
        # if not, add to end of file
        # format: "stem: {document, documentposition, terms, frequency}"
        pass