import urllib.request
import re
from bs4 import BeautifulSoup
import requests
import string
import csv

url = 'http://www.cnn.com/2017/04/14/politics/donald-trump-north-korea-mar-a-lago/index.html'
title = re.sub('.*/(.*)/index\.html',"\g<1>",url)
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
links = soup.select('div.zn-body__paragraph')
strlist = []
freq = {}
exclude = set(string.punctuation)
exclude.discard("'")
exclude.discard('-')
for lstring in links:
    newstr = str(lstring)
    newstr = re.sub('<.*?>', '', newstr)
    s = ''.join(ch for ch in newstr if ch not in exclude)
    strlist.append(s)

for lstring in strlist:
    for word in lstring.split():
        w = word.lower()
        if w in freq.keys():
            freq[w] += 1
        else:
            freq[w] = 1
with open('cnn-{}.csv'.format(title),'w') as f:
    w = csv.writer(f)
    for key, value in freq.items():
        w.writerow([key,value])

#print(links)
#print(soup.prettify())
