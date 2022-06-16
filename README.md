# Spidey Search
Spidey Search is a fully functional search engine built from the ground up and able to handle hundreds of thousands of documents or web pages. It consists of a crawler, an indexer, and a search interface.

### Crawl
The crawler can be used to create or update the corpus. It obeys the robots.txt file of the subdomain being crawled. It avoids web traps using various methods including comparing webpage footprints and detecting URL patterns. It can detect webpages with valuable text information and blacklist low information and error webpages.

### Index
The indexer is used to build an inverted index using the corpus. It is written in Python. It first filters the crawled data by detecting and eliminating duplicate pages and extracting the text content and positions of important tags. It then builds index files for different n-grams. Small portions of the index are offloaded in the indexing process and combined at the end using the k-way merge algorithm, allowing the indexer to have a smaller, adjustable memory footprint. The documents for each term in the index files are sorted using their adjusted tf-idf score which considers important HTML tags.

### Query
The search engine allows the user to search using a web interface that communicates with a REST API to retrieve search results.
The search engine finds relevant pages by applying intersections and unions on appropriate term document lists. Since the term documents are sorted by their scores, a subset of the documents for each term can be retrieved for intersecting, allowing for faster query times. The ranks of the results are adjusted based on the bigram index and cosine similarity with the query text to enhance search results.
