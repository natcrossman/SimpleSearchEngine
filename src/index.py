## @package index.py
# Index structure:
# The Index class contains a list of IndexItems, stored in a dictionary type for easier access
# each IndexItem contains the term and a set of PostingItems
# each PostingItem contains a document ID and a list of positions that the term occurs
#

#    Within a document collection, we assume that each document has a unique
#serial number, known as the document identifier (docID ). During index construction,
#we can simply assign successive integers to each new document
#when it is first encountered. 
#
#The input to indexing is a list of normalized
#tokens for each document, which we can equally think of as a list of pairs of
#SORTING term and docID (NOTE Sort BOTH). The core indexing step is sorting this list
#so that the terms are alphabetical. Multiple occurrences of the same term from the same
#document are then merged And we increase TF. Instances of the same term are then grouped,
#and the result is split into a dictionary and postings.
#Since a term generally occurs in a number of documents,
#this data organization already reduces the storage requirements of
#the index. 

#The dictionary also records some statistics, such as the number of
#documents which contain each term (the document frequency, which is here
#also the length of each postings list). This information is not vital for a basic
#Boolean search engine, but it allows us to improve the efficiency of the search engine at query time, 
#and it is a statistic later used in many ranked retrieval
#models. 
#
#The postings are secondarily sorted by docID. This provides
#the basis for efficient query processing. This inverted index structure is essentially
#without rivals as the most efficient structure for supporting ad hoc
#text search
#
#@copyright     All rights are reserved, this code/project is not Open Source or Free
#@bug           None Documented     
#@author        Nathaniel Crossman & Adam
#


"""Internal libraries"""
import doc
from util import Tokenizer
from cran import CranFile

"""Outside libraries"""
import sys
import json
import operator
import collections


##
#This is our posting clas. 
# @brief The job of this class is to  store the document ID, 
# the position where the term occurred in the document, 
# and the frequency of each term in each document.
# 
#In Short, Each postings list stores the list of documents
# in which a term occurs, and may store other information such as the term frequency
# or the position(s) of the term in each document.
# We don't technically need to store the frequency as we can calculate it by looking at the positions
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
        self.docID      = docID
        self.positions  = []
        #  self.termFrequency = 0 not need
    
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
    #   @brief         This method returns the term freq by count the
    #                  positions this term appeared in a given document.
    #    Why?: A Boolean model only records term presence or absence, but often we
    #    would like to accumulate evidence, givingmoreweight to documents that
    #    have a term several times as opposed to ones that contain it only once. To
    #    be able to do this we need term frequency information TERM FREQUENCY (the number of times
    #    a term occurs in a document) in postings lists
    #   @param         self
    #   @param         positions
    #   @return        int frequency
    #   @exception     None
    ## 
    def term_freq(self):
      return  len(self.positions)

    # ##
    # #   @brief         This method increase the increase_term_frequency
    # #   @param         self
    # #   @param         positions
    # #   @return        int frequency
    # #   @exception     None
    # ## 
    # def increment_term_frequency(self):
    #     self.termFrequency += 1


##
# @brief     
#
# @bug       None documented yet   
#
class IndexItem:
     ##
    #    @param         self
    #    @param         term
    #    @return        None
    #    @brief         The constructor. 
    #    @exception     None documented yet
    ##
    def __init__(self, term):
        self.term               = term
        self.posting            = {} #postings are stored in a python dict for easier index building
        self.sorted_postings    = [] # may sort them by docID for easier query processing
        self.sorted_dict        = {} #not sure if need
    
    ##
    #   @brief         This method adds a term position, for a Document to the postings list.
    # If this is the first time a document has been added to the posting list,
    # the method creates a new posting (with docID) 
    # and then adds this the position the term was in the document.
    # Otherwise, This method just adds the new position.
    #
    #   @param         self
    #   @param         docid
    #   @param         pos
    #   @return        None
    #   @exception     None
    ## 
    def add(self, docid, pos):
        ''' add a posting, changes my ncc'''
        key = self.posting.keys() #list of all keys
        if docid not in key:
            self.posting[docid] = Posting(docid)
        self.posting[docid].append(pos)
        #Removed old code, as python 3 does not have has_key.
        # if not self.posting.has_key(docid):
        #     self.posting[docid] = Posting(docid)
        # self.posting[docid].append(pos)

    ##
    #   @brief         This method sort the posting list by document ID for more efficient merging. 
    # And also sort each posting positions
    # 
    #
    #   @param         self
    #   @return        sorted posting list and sorted dict posting list
    #   @exception     None
    ## 
    def sort(self):
        ''' 
        sort by document ID for more efficient merging. For each document also sort the positions
        Firt sort all posting positions
        then sort doc id 
        also creat new sorted dict. // not sure if need but why not
        '''
        for key, postingTemp in self.posting.items():
            postingTemp.sort()

        self.sorted_postings    = sorted(self.posting.items(), key=operator.itemgetter(0))
        self.sorted_dict        = collections.OrderedDict(self.sorted_postings)
        return self.sorted_postings , self.sorted_dict


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
        self.__items     = {} # list of IndexItems
        self.__nDocs     = 0  # the number of indexed documents
        self.__tokenizer = Tokenizer()

    ##
    #   @brief     This method is designed to index a docuemnt, using the simple SPIMI algorithm, 
    #              but no need to store blocks due to the small collection we are handling. 
    #              Using save/load the whole index instead
    # 
    #       ToDo: indexing only title and body; use some functions defined in util.py
    #       (1) convert to lower cases,
    #       (2) remove stopwords,
    #       (3) stemming
    #
    #   @param         self
    #   @param         Doc
    #   @return        None
    #   @exception     None
    ## 
    def indexDoc(self, doc): # indexing a Document object
        #Concatenate document title
        newDoc              = doc.title + " " + doc.body
        docID               = doc.docID
        full_stemmed_list   = self.__tokenizer.transpose_document_tokenized_stemmed(newDoc)
        
        for position, term in enumerate(full_stemmed_list):
            if self.__items.get(term) !=None:
                self.__items[term].add(docID, position)
            else:
                #key does not exists in dict
                newPosting                          = Posting(docID)
                newPosting.append(position)
                self.__items[term]                  = IndexItem(term)
                self.__items[term].posting[docID]   = newPosting


    def sort(self):
        ''' sort all posting lists by docID'''
        for term, posting in self.__items.items():
           print(posting)
        #ToDo

    def find(self, term):
        return self.__items[term]

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

    #doc = sys.argv[1]
    filePath = "./CranfieldDataset/cran.all"
    invertedIndexer = InvertedIndex()
    data = CranFile(filePath)
    for doc in data.docs:
        invertedIndexer.indexDoc(doc)


if __name__ == '__main__':
    #test()
    indexingCranfield()
