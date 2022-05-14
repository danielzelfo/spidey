List of extensions in page_data:
```
{'rle', 'tsv', '07055', 'grm', 'mak', 'php', 'htm', 'r', 'frk/', 'vg', 'svn/', 'md', 'htm~', 'cnt', 'LOG', 'tc', 'rkt', 'fig', 'cgi', 'ipynb', 'html', 'patch', 'conf', 'txt~', 'pbtxt', 'sty', 'Rmd', 'hash', 'fai', 'gff3', 'npy', 'txt', 'x', 'temp', 'defs', 'cls', 'pyc', 'sas', 'map', 'th', 'SMA', 'clw', 'in', 'svg', 'dsp', 'phtml', 'R', 'prefs', 'rc', 'splay', 'ff', 'orig', 'sln', 'lca', 'dsw', 'shtml', 'plg', 'ss', 'pyg', 'words', '5/', '0/', 'sql', 'mht', 'ncb', 'intro', 'model', 'rc2', 'bib', 'lif', 'war', 'hs', 'html~', '1/', 'TXT', 'cp', 'mzn', 'wmf', 'inc', 'MF', 'dirs', 'tmpl', 'def', 'cdb', 'mcs', 'emx', 'pq', 'xml', 'pov', 'opt', 'als', 'NO_EXTENSION', 'sift', 'log', '22', 'git/', 'cc', 'html/', 'path', 'fasta', 'prn'}
```


long page:
page_data/data/DEV/mondego_ics_uci_edu/95c3f9dc662f1fe7ed6982cf896e810756fda1098742bf09659f05a33d9c790a.json

todo:

Filter:
    replace (\s+, " ")

search title (stored in docInfo.txt) [higher importance]

Final project notes:
Ranking (during indexing and query) 
    - tf * idf score (term freq, inverse doc frequency)
    - index by score, take top 10 of the tokens, do intersection, and rank again


Bigrams
Page Similarity

expand contractions while tokenizing for index



important tags: ex <b></b>
    options:
    1. separate extract text to seperate directories?
    ```
        important/{...}.json
        rest/{...}.json
    ```

    2. save spans of important text in extracted text?

wider search (for not enough results)
    SET UNION instead of INTERSECTION?

    search stop words?
        needs sorted index