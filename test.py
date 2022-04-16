import re

x = "https://www.ics.uci.edu/ugrad/honors/index.php/policies/overview/overview/degrees/policies/policies/policies/policies/sao/sao/SAO_News_and_Updates.php"
key = "policies"
blacklisturl = re.escape(x[:x.find(key)])

print(blacklisturl)