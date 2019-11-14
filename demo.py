#!/usr/bin/python

###########################################################
# Subject: Word processing
# Topic: Extraction of "nice" text in Polish from a website
# Credits: Krystian Hoczkiewicz | 452141
# University: Adam Mickiewicz University, Poznań, Poland
# Details: More specific info at the very bottom
###########################################################

import sys, getopt # Args Libs
import urllib.request # URL-handling lib
from inscriptis import get_text # HTML-to-text lib
import ssl # SSL Lib
import re # Regex Lib

abbreviations = ['np[.]', 'ang[.]', 'm.in[.]', 'r[.]', 'inż[.]']
substitutions = [['[&dot]', '.']]
punctuationFailures = [['( ', '('], [' )',')'], [' .','.'], [' ,',','], [' :',':']]

# Eliminates annotations like "[ wiki | page | example ]"
def eliminateAnnotations(text):
    return re.sub('\[.*?\]', '', text)
    
# Catches abbreviations pretending to be end of sentence
def catchAbbreviations(text):
    replacedText = text
    for abbreviation in abbreviations:
        replacedText = re.sub(abbreviation, abbreviation.replace('.', '&dot'), replacedText)
    return replacedText
    
# Matches proper sentences with specific regex
def matchSentences(text):
    return re.findall("[A-Z].*?[\.!?] ", text, re.MULTILINE | re.DOTALL)

# Eliminates substitutions of unwanted symbols
def cleanUpSentence(sentence):
    replacedSentence = sentence
    for substitution in substitutions:
        replacedSentence = sentence.replace(substitution[0], substitution[1])
    for punctuationFailure in punctuationFailures:
        replacedSentence = replacedSentence.replace(punctuationFailure[0], punctuationFailure[1])
    return replacedSentence
    
# Eliminates wiki footer
def eliminateWikiFooter(line):
    return re.sub('.*\*.*?\*.*', '', line)
    
# Splits Interia click-baits
def splitInteriaBaits(line):
    return line.replace(' * ', '.\n')

# Function gets list of the sentences from specific website
def getSentences(website):

    print('Setting certificate...')
    ssl._create_default_https_context = ssl._create_unverified_context

    print('Decoding website...')
    html = urllib.request.urlopen(website).read().decode('utf-8') 

    print('Getting website\'s text...')
    text = get_text(html).replace('\n', '')
        
    print('Eliminating annotations...')
    text = eliminateAnnotations(text)

    print('Removing unnecessary whitespaces...')
    while '  ' in text:
        text = text.replace('  ', ' ')
    
    print('Catching abbreviations...')
    text = catchAbbreviations(text)

    print('Matching sentences...')
    return matchSentences(text)

# File-streaming function
def writeSentencesToFile(sentences, outputfile):
    outputStream = open(outputfile,"w+", encoding='utf-8')
    
    print('Cleaning sentences up...')
    for sentence in sentences:
        newLine = splitInteriaBaits(eliminateWikiFooter(cleanUpSentence(sentence)))
        if newLine is not '':
            outputStream.write(newLine + '\n')

# Main function to process args and possible exceptions
def main(argv):
   website = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hw:o:",["website=","outputfile="])
   except getopt.GetoptError:
      print('demo.py -w <website> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('demo.py -w <website> -o <outputfile>')
         sys.exit()
      elif opt in ("-w", "--website"):
         website = arg
      elif opt in ("-o", "--outputfile"):
         outputfile = arg
         
   print('Website is ' + website)
   print('Output file is ' + outputfile)
   print('Processing...')
   
   sentences = getSentences(website)
   writeSentencesToFile(sentences, outputfile)
   
   print('Output has been written successful.')
   
###############################################################
# Python 3.7.3
# Requirements:
# * inscriptis>=0.0.4.1.1
# * urllib3>=1.24.2
# Usage - .\demo.py -w website -o outputfile
# Where -w is and adress of website we want to import text from
# eg. https://forbes.pl
# and -o is an output file where we want to write text into.
###############################################################

if __name__ == "__main__":
   main(sys.argv[1:])