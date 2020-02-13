## @package index.py
# Index structure:
# The Index class contains a list of IndexItems, stored in a dictionary type for easier access
# each IndexItem contains the term and a set of PostingItems
# each PostingItem contains a document ID and a list of positions that the term occurs
#    
#@copyright     All rights are reserved, this code/project is not Open Source or Free
#@bug           None Documented     
#@author        Nathaniel Crossman & Adam
#


"""NEED TO WORK ON """
import util 
import doc
from cran import CranFile

"""OTHER"""
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

##
#This is our posting clas. 
# @brief The job of this class is to  store the document ID, 
# the position where the term occurred in the document, 
# and the frequency of each term in each document.
# 
#In Short, Each postings list stores the list of documents
# in which a term occurs, and may store other information such as the term frequency
# or the position(s) of the term in each document.
#
# @bug       None documented yet   
#
class Posting:
    ##
    #    @param         self
    #    @param         docID
    #    @return        None
    #    @brief         The constructor. 
    #    @exception     None documented yet
    ##
    def __init__(self, docID):
        self.docID = docID
        self.positions = []
        self.termFrequency = 0 #This is term frequency not document frequency
        #We need frequency
   
    ##
    #   @brief         This method append a positions to our array
    #   @param         self
    #   @param         pos
    #   @return        None
    #   @exception     None
    ## 
    def append(self, pos):
        self.positions.append(pos)

    ##
    #   @brief         This method sorts the positions array
    #   @param         self
    #   @return        None
    #   @bug           This need to be tested
    #   @exception     None
    ## 
    def sort(self):
        ''' sort positions'''
        self.positions.sort()

    ##
    #   @brief         This method combines/merges two conditional array.
    #   @param         self
    #   @param         positions
    #   @return        None
    #   @exception     None
    ## 
    def merge(self, positions):
        self.positions.extend(positions)
    ##
    #   @brief         This method returns the term freq
    #   @param         self
    #   @param         positions
    #   @return        int frequency
    #   @exception     None
    ## 
    def term_freq(self):
        return self.termFrequency

    
    ##
    #   @brief         This method increase the increase_term_frequency
    #   @param         self
    #   @param         positions
    #   @return        int frequency
    #   @exception     None
    ## 
    def increment_term_frequency(self):
        self.termFrequency += 1

##
# @brief     
#
# @bug       None documented yet   
#
class IndexItem:
     ##
    #    @param         self
    #    @param         topicName
    #    @return        None
    #    @brief         The constructor. 
    #    @exception     None documented yet
    ##
    def __init__(self, term):
        self.term = term
        self.posting = {} #postings are stored in a python dict for easier index building
        self.sorted_postings= [] # may sort them by docID for easier query processing

    def add(self, docid, pos):
        ''' add a posting'''
        if not self.posting.has_key(docid):
            self.posting[docid] = Posting(docid)
        self.posting[docid].append(pos)

    def sort(self):
        ''' sort by document ID for more efficient merging. For each document also sort the positions'''
        # ToDo

##
# @brief     
#
# @bug       None documented yet   
#
class InvertedIndex:
    ##
    #    @param         self
    #    @param         topicName
    #    @return        None
    #    @brief         The constructor. 
    #    @exception     None documented yet
    ##
    def __init__(self):
        self.items = {} # list of IndexItems
        self.nDocs = 0  # the number of indexed documents


    def indexDoc(self, doc): # indexing a Document object
        ''' indexing a docuemnt, using the simple SPIMI algorithm, but no need to store blocks due to the small collection we are handling. Using save/load the whole index instead'''

        # ToDo: indexing only title and body; use some functions defined in util.py
        # (1) convert to lower cases,
        # (2) remove stopwords,
        # (3) stemming


    def sort(self):
        ''' sort all posting lists by docID'''
        #ToDo

    def find(self, term):
        return self.items[term]

    def save(self, filename):
        ''' save to disk'''
        # ToDo: using your preferred method to serialize/deserialize the index

    def load(self, filename):
        ''' load from disk'''
        # ToDo

    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''
        #ToDo: return the IDF of the term

    # more methods if needed


def test():
    ''' test your code thoroughly. put the testing cases here'''
    print('Pass')

def indexingCranfield():
    #ToDo: indexing the Cranfield dataset and save the index to a file
    # command line usage: "python index.py cran.all index_file"
    # the index is saved to index_file

    print('Done')

if __name__ == '__main__':
    #test()
    indexingCranfield()
