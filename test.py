from lxml import html
import requests
from urllib.parse import urlparse, urljoin, urldefrag
import timeit
import numpy as np

url = "https://en.wikipedia.org/wiki/Shor%27s_algorithm"


page = requests.get(url)

tree = html.fromstring(page.content)  
  
# Get element using XPath
x = tree.xpath('.//a[@href]/@href')

f = lambda x: urldefrag(urljoin(url, x))[0] #absolute_url(x)
vf = np.vectorize(f)

def test_map(x, n):
    t = timeit.timeit(
        'map(f, x)',
        'from __main__ import x, f', number=n)
    print('map: {0:.3f}'.format(t))

def test_direct(x, n):
    t = timeit.timeit(
        'set([f(i) for i in x])',
        'from __main__ import x, f', number=n)
    print('direct: {0:.3f}'.format(t))

def test_vectorized(x, n):
    t = timeit.timeit(
        'set(vf(x))',
        'from __main__ import x, vf', number=n)
    print('vectorized: {0:.3f}'.format(t))

n = 1000
# test_direct(x, n)      # 0.265
# test_vectorized(x, n)  # 2.906
test_map(x,n)