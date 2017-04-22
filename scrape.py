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
# binary search
from bisect import bisect_left

# Supported news sources. These are also associated with indices
CONST_NYTIMES    =    0
CONST_CNN         =    1
CONST_FOXNEWS    =    2

# Title specifiers. These are used to extract each source's title.
# Index 0: NY Times
# Index 1: CNN
# Index 2: Fox News 
CONST_TITLE_SPECS    =    ['\.html.*', '/index\.html', '\.html']

# HTML paragraph specifiers. These are used to extract each source's page content.
# Index 0: NY Times
# Index 1: CNN
# Index 2: Fox News
CONST_PARA_SPECS    =    ['p.story-body-text.story-content', 'div.zn-body__paragraph', 'div.article-text']

# CSV file names. These are file names to be used when exporting the content as a CSV file
# Index 0: NY Times
# Index 1: CNN
# Index 2: Fox News
CONST_CSV_NAMES      =    ['NYTIMES','CNN','FOXNEWS']


# If the system is Daniel's, we need to exclude the special characters <> and <>
CONST_IS_DANIELS_SYS    =    False

# Current directory we are under.
CUR_DIR        =    "."

# Global lists for lexicons
CONST_POS_WORDS        = []
CONST_NEG_WORDS        = []

# Name of file that stores the summary of the link parse
CONST_FN_SUMMARY    =    'summary.txt'
# Name of file that stores all of the topics (the head)
CONST_FN_HEAD        =    'Topics'

"""
Function name: 
    parse_html

Parameters: 
@param    url      String      Contains the url to parse 
@param    siteInd    Int         Identifies the news source to use. It is an index based on 
                     the constants: CONST_NYTIMES, CONST_CNN, CONST_FOXNEWS

Description:
    Parses a NY Times, CNN, or Fox News webpage for information in the article
"""
def parse_html( url, siteInd):
    # extract title from page url    
    title = re.sub('.*/(.*)'+CONST_TITLE_SPECS[siteInd],"\g<1>",url)
    # get page and make it nice
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # grab part of page we want
    links = soup.select(CONST_PARA_SPECS[siteInd])
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

    # Keep track of counts we are interested in
    posCount = 0
    negCount = 0
    numWords = 0
    uniqueWords = 0
    posWords = []
    negWords = []
    # break into words and update freqencies
    for lstring in strlist:
        for word in lstring.split():
            numWords += 1
            w = word.lower()
            if w in freq.keys():
                freq[w] += 1
            else:
                freq[w] = 1
                uniqueWords += 1
            # Count towards positive/negative words
            if binary_search(CONST_POS_WORDS,w) != -1:
                posCount += 1
                posWords.append(w)
            if binary_search(CONST_NEG_WORDS,w) != -1:
                negCount += 1
                negWords.append(w)
    if "--" in freq.keys():
        del freq["--"]
    # write the frequencies as a csv
    with open(os.path.abspath(os.path.join(CUR_DIR,CONST_CSV_NAMES[siteInd]+'.csv')),'w') as f:
        w = csv.writer(f)
        for key, value in freq.items():
            w.writerow([key,value])
    # Write to the summary.txt file
    with open(os.path.abspath(os.path.join(CUR_DIR,CONST_FN_SUMMARY)),'a') as f:
        f.write('News source: {}\n'.format(CONST_CSV_NAMES[siteInd]))
        f.write('URL Link: {}\n'.format(url));
        f.write('Total word count: {}\n'.format(numWords))
        f.write('Unique word count: {}\n'.format(uniqueWords))
        f.write('Positive word count: {}\n'.format(posCount))
        f.write('Negative word count: {}\n'.format(negCount))
        f.write('Positive words: {}\n'.format(posWords))
        f.write('Negative words: {}\n'.format(negWords))
        f.write('\n')

"""
Function name:
    parse_link
    
Parameters:
@param        url        String        The URL to parse for HTML

Description:
    Helper function to identify which news source we are using
"""
def parse_link(url):
    if(re.search("foxnews\.com", url)):
        parse_html( url.strip(), CONST_FOXNEWS )
    elif(re.search("cnn\.com", url)):
        parse_html( url.strip(), CONST_CNN )
    elif(re.search("nytimes\.com", url)):
        parse_html( url.strip(), CONST_NYTIMES )

"""
Function name: 
    create_dirs

Parameters: 
@param    fileName      String      Contains the fileName for the list of links
                                    we are to parse

Description:
    Parses a text file for links to parse.  
    
    The text file contains the following structure:
    ---
    DIRECTORY_NAME_BASED_ON_TOPIC
    http://cnn.com/<article>
    http://foxnews.com/<article>
    http://nytimes.com/<article>

    DIRECTORY_NAME_BASED_ON_TOPIC
    http://cnn.com/<article>
    http://foxnews.com/<article>
    http://nytimes.com/<article>
    ---    
"""
def create_dirs( fileName ):
    global CUR_DIR
    
    # Confirm the head directory is created
    if not os.path.exists(CONST_FN_HEAD):
        os.makedirs(CONST_FN_HEAD)
    
    with open(fileName) as f:
        for line in f:
            # Get rid of all newline characters
            line = line.strip('\n')
            if not re.search("http", line) and len(line) > 0:
                # If the line is not a link, then it is a topic name
                newDir = os.path.join(CONST_FN_HEAD,line);
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                CUR_DIR = newDir
                
                # Delete the summary.txt file's contents if it already exists
                if os.path.exists(os.path.join(CUR_DIR,CONST_FN_SUMMARY)):
                    open(os.path.join(CUR_DIR,CONST_FN_SUMMARY),'w').close()
            else:
                # The line is a link, so let's parse it
                parse_link(line)

"""
Function name: 
    binary_search

Parameters: 
@param    a      List      Contains the list to search over
@param    x      Int       The target we are searching for
@param    lo     Int       The smallest index within the list we are searching over
@param    hi     Int       The largest index within the list we are searching over

Description:
    Parses a NY Times, CNN, or Fox News webpage for information in the article
"""
def binary_search(a,x,lo=0,hi=None):
    hi = hi or len(a)  # hi defaults to len(a)   
    pos = bisect_left(a, x, lo, hi)  # find insertion position
    return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end
    
"""
Function name: 
    parse_lexicons

Parameters: 
@param    fileName      String      Contains the name of the file to parse
@param    array         List        The place to store the list of words/lexicons

Description:
    Parses a file for a list of words
"""    
def parse_lexicons(fileName, array):    
    with open(fileName) as f:
        for line in f:
            line = line.strip('\n')
            # The files we are using uses semicolons as comments, remove them
            if ';' not in line and len(line) > 0:
                array.append(line)
                
"""
Function name:
    main

Parameters:
None

Description:
    Main function to call
"""    
def main():
    # Parse the list of positive and negative words into their respective lists
    global CONST_POS_WORDS, CONST_NEG_WORDS
    parse_lexicons('positive-words.txt', CONST_POS_WORDS)
    parse_lexicons('negative-words.txt', CONST_NEG_WORDS)
    
    # Create the directories necessary to begin parsing
    create_dirs( "links.txt" )

if __name__ == '__main__':
    main()
