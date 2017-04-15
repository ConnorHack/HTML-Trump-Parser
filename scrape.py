# extract article title and remove html tags
import re
# get text from specific html tags
from bs4 import BeautifulSoup
# get the web page content
import requests
# string.punctuation
import string
# write the output csv file
import csv


def parse_cnn( url ):
    '''
    parse_cnn parses a cnn webpage for the information in an article.
    @param url the string representation of the cnn url
    '''
    # extract title from page url
    title = re.sub('.*/(.*)/index\.html',"\g<1>",url)
    # get page and make it nice
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # grab part of page we want
    links = soup.select('div.zn-body__paragraph')
    strlist = []
    # the dictionary mapping word->freqency
    freq = {}
    # set of punctuation to strip, not including ' and -
    exclude = set(string.punctuation)
    exclude.discard("'")
    exclude.discard('-')
    # strip html tags and punctuation
    for lstring in links:
        newstr = str(lstring)
        newstr = re.sub('<.*?>', '', newstr)
        s = ''.join(ch for ch in newstr if ch not in exclude)
        strlist.append(s)

    # break into words and update freqencies
    for lstring in strlist:
        for word in lstring.split():
            w = word.lower()
            if w in freq.keys():
                freq[w] += 1
            else:
                freq[w] = 1
    # write the frequencies as a csv
    with open('cnn-{}.csv'.format(title),'w') as f:
        w = csv.writer(f)
        for key, value in freq.items():
            w.writerow([key,value])

def parse_cnn_file( filename ):
    '''
    parse_cnn_file parses a file containing cnn links, one on each line.
    @param filename the name of the file to read.
    '''
    with open(filename) as f:
        for line in f:
            parse_cnn( line.strip() )

parse_cnn_file( "cnn.txt" )
