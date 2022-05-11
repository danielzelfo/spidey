import json
import os
from HTMLParser import HTMLParser
from alive_progress import alive_bar

class Filter:
    def __init__(self, files, textContentSavePath, run_log):
        self.files = files
        self.textContentSavePath = textContentSavePath
        self.run_log = run_log
        self.htmlParser = HTMLParser()
        self.countSuccessFul = 0

    def filter_file(self, filepath, docInfoFile):
        with open(filepath) as f:
            data = json.load(f)
            content = data["content"]
            encoding = data["encoding"]
            url = data["url"]

        # safely extract text
        try:
            title, textContent = self.htmlParser.extract_info(content, encoding, url)

            # save text content to disk
            filename = os.path.split(filepath)[-1]
            saveFilePath = os.path.join(self.textContentSavePath, filename)
            with open(saveFilePath, "w") as f:
                f.write(textContent)
            
            # save document Info
            docInfoFile.write(f"{json.dumps([title, url, filename])}\n")

            self.countSuccessFul += 1
        except Exception as e:
            print(f"Extract text error for {url}: {e}")
            if not self.run_log is None:
                self.run_log.write(f"Extract text error for {url}: {e}\n")
            return
    
    def run_filter(self):
        with open("docInfo.txt", "w") as docInfoFile:
            with alive_bar(len(self.files), force_tty=True) as bar:
                for filepath in self.files:
                    self.filter_file(filepath, docInfoFile)
                    bar()
        with open("num_documents.txt", "w") as f:
            f.write(str(self.countSuccessFul))
        