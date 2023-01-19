# Spidey Search
Spidey Search is a powerful and efficient search engine that can handle large volumes of documents or web pages. It includes a web crawler, an indexer, and a user-friendly search interface, all built from the ground up.

### Crawling
The crawler is designed to create or update the corpus of documents that the search engine indexes. It respects the robots.txt file of the websites it crawls, and uses various methods to avoid common web traps. These include comparing webpage footprints and detecting URL patterns. Additionally, the crawler is able to detect web pages with valuable text information and blacklist low-quality or error pages.

### Indexing
The indexer, written in Python, is responsible for building the inverted index that powers the search engine. It filters the crawled data by eliminating duplicate pages, extracting the text content, and determining the positions of important tags. The indexer then builds index files for different n-grams, using a k-way merge algorithm to combine smaller portions of the index as it is built. This allows for a more efficient use of memory. The documents are sorted using an adjusted tf-idf score, which takes into account the importance of HTML tags.

### Searching
The search engine allows users to search for relevant documents using a web interface that communicates with a REST API. The search engine finds relevant pages by applying intersections and unions on appropriate term-document lists. The term-documents are sorted by their scores, allowing for faster query times. The search results are ranked using bigram index and cosine similarity with the query text, to enhance the relevance of the results.

## Getting Started
To get started with Spidey Search, please refer to the [backend](/backend/) and [frontend](/frontend/) README files for specific instructions on how to run and use the system.
