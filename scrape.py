'''
scrape.py reads in a text file, links.txt, that contains cnn and fox news links.
The script then parses each webpage, reading the article text, stripping punctuation,
creating a hashmap of word->word frequency, finally outputting it as a csv file in 
a sub folder called cnn/fox, depending on the article website.

To run, first ensure you have installed requests and bs4:

    sudo pip3 install requests bs4

then run the script as follows:

    python3 scrape.py

NOTE: if the file links.txt does not exist or is incorrectly formatted, the program
will likely crash.
'''
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
# make folders
import os

def parse_fox( url ):
    '''
    parse_fox parses a fox news webpage for the information in an article.
    @param url the string representation of the fox news url
    '''
    # extract title from page url
    title = re.sub('.*/(.*)\.html',"\g<1>",url)
    # get page and make it nice
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # grab part of page we want
    links = soup.select('div.article-text')
    strlist = []
    # the dictionary mapping word->freqency
    freq = {}
    # set of punctuation to strip, not including ' and -
    exclude = set(string.punctuation)
    exclude.discard("'")
    exclude.discard('-')
    exclude.add("“")
    exclude.add("”")
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
    if "--" in freq.keys():
        del freq["--"]
    # write the frequencies as a csv
    with open('fox/{}.csv'.format(title),'w') as f:
        w = csv.writer(f)
        for key, value in freq.items():
            w.writerow([key,value])

def parse_cnn( url ):
    '''
    parse_cnn parses a cnn webpage for the information in an article.
    @param url the string representation of the cnn url
    '''
    # extract title from page url
    title = re.sub('.*/(.*)/(index\.html|)',"\g<1>",url)
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
    if "--" in freq.keys():
        del freq["--"]
    # write the frequencies as a csv
    with open('cnn/{}.csv'.format(title),'w') as f:
        w = csv.writer(f)
        for key, value in freq.items():
            w.writerow([key,value])

def parse_nyt( url ):
    '''
    parse_nyt parses a nyt webpage for the information in an article.
    @param url the string representation of the nyt url
    '''
    # extract title from page url
    title = re.sub('.*/(.*)\.html.*',"\g<1>",url)
    # get page and make it nice
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # grab part of page we want
    links = soup.select('p.story-body-text.story-content')
    strlist = []
    # the dictionary mapping word->freqency
    freq = {}
    # set of punctuation to strip, not including ' and -
    exclude = set(string.punctuation)
    exclude.discard("'")
    exclude.discard('-')
    exclude.add("“")
    exclude.add("”")
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
    if "--" in freq.keys():
        del freq["--"]
    # write the frequencies as a csv
    with open('nyt/{}.csv'.format(title),'w') as f:
        w = csv.writer(f)
        for key, value in freq.items():
            w.writerow([key,value])

def parse_file( filename ):
    '''
    parse_file parses a file containing cnn and/or foxnews links, one on each line.
    @param filename the name of the file to read.
    '''
    with open(filename) as f:
        for line in f:
            if(re.search("foxnews\.com", line)):
                parse_fox( line.strip() )
            elif(re.search("cnn\.com", line)):
                parse_cnn( line.strip() )
            elif(re.search("nytimes\.com", line)):
                parse_nyt( line.strip() )

def main():
    # make fox folder
    if not os.path.exists("fox"):
        os.makedirs("fox")
    # make cnn folder
    if not os.path.exists("cnn"):
        os.makedirs("cnn")
    parse_file( "links.txt" )
    # make nyt folder
    if not os.path.exists("nyt"):
        os.makedirs("nyt")
    parse_file( "links.txt" )

if __name__ == '__main__':
    main()
