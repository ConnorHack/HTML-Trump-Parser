import urllib.request
import re
from bs4 import BeautifulSoup
import requests
import string
import csv

response = requests.get('http://www.cnn.com/2017/04/14/politics/donald-trump-north-korea-mar-a-lago/index.html')
soup = BeautifulSoup(response.text, "html.parser")
links = soup.select('div.zn-body__paragraph')
strlist = []
freq = {}
for lstring in links:
    newstr = str(lstring)
    newstr = re.sub('<.*?>', '', newstr)
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in newstr if ch not in exclude)
    strlist.append(s)

for lstring in strlist:
    for word in lstring.split():
        w = word.lower()
        if w in freq.keys():
            freq[w] += 1
        else:
            freq[w] = 1
print(freq)
print(freq["trump"])
with open('cnn.csv','w') as f:
    w = csv.writer(f)
    for key, value in freq.items():
        w.writerow([key,value])

#print(links)
#print(soup.prettify())
