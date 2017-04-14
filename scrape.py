import urllib.request
import re
from bs4 import BeautifulSoup
import requests

response = requests.get('http://www.cnn.com/2017/04/14/politics/donald-trump-north-korea-mar-a-lago/index.html')
soup = BeautifulSoup(response.text, "html.parser")
links = soup.select('div.zn-body__paragraph')
for string in links:
    newstr = str(string)
    newstr = re.sub('<.*?>', '', newstr)
    print(newstr)
#print(links)
#print(soup.prettify())
