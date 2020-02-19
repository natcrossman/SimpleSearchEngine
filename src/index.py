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
        self.__docID      = docID
        self.__positions  = []
        #  self.termFrequency = 0 not need
    
    ##
    #   @brief         This method append a positions to our array
    #   @param         self
    #   @param         pos
    #   @return        None
    #   @exception     None
    ## 
    def append(self, pos):
        self.__positions.append(pos)

    ##
    #   @brief         This method sorts the positions array
    #   @param         self
    #   @return        None
    #   @bug           This need to be tested
    #   @exception     None
    ## 
    def sort(self):
        ''' sort positions'''
        self.__positions.sort()

    ##
    #   @brief         This method combines/merges two conditional array.
    #   @param         self
    #   @param         positions
    #   @return        None
    #   @exception     None
    ## 
    def merge(self, positions):
        self.__positions.extend(positions)
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
      return  len(self.__positions)

    ##
    #   @brief         This method 
    #   @param         self
    #   @return        int frequency
    #   @exception     None
    ## 
    def to_Json(self):
        return {self.__docID: self.__positions}
  

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
        self.__term             = term
        self.__posting          = {} #postings are stored in a python dict for easier index building
        self.__sorted_postings  = [] # may sort them by docID for easier query processing
        self.__sorted_dict      = {} #not sure if need

    def set_posting_list(self, docID, posting):
        self.__posting[docID] = posting
    def get_posting_list(self):
        return self.__posting

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
        key = self.__posting.keys() #list of all keys
        if docid not in key:
            self.__posting[docid] = Posting(docid)
        self.__posting[docid].append(pos)
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
    def return_sorted_posting(self):
        ''' 
        sort by document ID for more efficient merging. For each document also sort the positions
        Firt sort all posting positions
        then sort doc id 
        also creat new sorted dict. // not sure if need but why not
        '''
        for key, postingTemp in self.__posting.items():
            postingTemp.sort()

        self.__sorted_postings    = sorted(self.__posting.items(), key=operator.itemgetter(0))
        self.__sorted_dict        = collections.OrderedDict(self.__sorted_postings)
        return self.__sorted_postings , self.__sorted_dict

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
        for key, postingTemp in self.__posting.items():
            postingTemp.sort()

        self.__sorted_postings    = sorted(self.__posting.items(), key=operator.itemgetter(0))
        self.__posting            = collections.OrderedDict(self.__sorted_postings)
    ##
    #   @brief         This method prints a post to strng
    #   @param         self
    #   @return        int frequency
    #   @exception     None
    ## 
    def posting_list_to_string(self):
        listOfShit = []
        for docID, post in  self.__posting.items():
            listOfShit.append(post.to_Json())
        return listOfShit
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
    #   @brief     This method return the total number of doc in our data set
    #
    #   @param         self
    #   @param         Doc
    #   @return        None
    #   @exception     None
    ## 
    def get_total_number_Doc(self):
        return self.__nDocs
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
                self.__items[term].set_posting_list(docID, newPosting)
        self.__nDocs += 1
        #self.sort() # not need as each posting list is sorted by default. Ths to data
        # if self.__nDocs == 2:
        #     self.save("dfd")
        #     self.load("dfd")
        
    ##
    #   @brief     This method Sorts all posting list by document ID. 
    #              NOTE: This method seems redundant as by default all postings list document IDs will be in order. 
    #                    Since documents are read in in a particular order. 
    #   @param         self
    #   @return        None
    #   @exception     None
    ## 
    def sort(self):
        ''' sort all posting lists by docID'''
        for term, posting in self.__items.items():
          posting.sort()
        #ToDo
   

    ##
    #   @brief     This method sorts all indexing terms in our index 
    #
    #   @param         self
    #   @return        None
    #   @exception     None
    ## 
    def sort_terms(self):
        ''' sort all posting lists by docID'''
        return collections.OrderedDict(sorted(self.__items.items(), key=operator.itemgetter(0)))
        #
  
    ##
    #   @brief     This method finds a term in the indexing and returns its posting list
    #
    #   @param         self
    #   @return        None
    #   @exception     None
    ## 
    def find(self, term):
        return self.__items[term]


    ##
    #   @brief     This method Serializes the inverted index to a json format and 
    #              clears the Memory that holds this dictionary
    #
    #   @param         self
    #   @param         filename
    #   @return        None
    #   @exception     None
    ## 
    def save(self, filename):
        write_stream = open(filename, 'w')
        listTerm = self.sort_terms()
        dictMain = {}
        listInfo =[]

        for term, postingList in listTerm.items():
           dictMain[term] = postingList.posting_list_to_string()
        listInfo.append({"nDoc": self.get_total_number_Doc()})
        listInfo.append({"Data":dictMain})
        write_stream.write(json.dumps(listInfo, indent=2, sort_keys=True))
        # with open(filename, 'w') as outfile:
        #     json.dump(obj=self.__items, default=self.dumper, fp=outfile, indent=3)
        # self.__items.clear()

    def dumper(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

    ##
    #   @brief     This method deserializes a json file in a object by reallocating the self.__items
    #
    #   @param         self
    #   @param         filename
    #   @return        None
    #   @exception     None
    ## 
    def load(self, filename):
        with open(filename) as json_file:
            return json.load(json_file)


    
    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''


        # TF (Number of time the word occurs in the text) / (Total number of words in text)
        #ToDo: return the IDF of the term

        # IDF = (Total number of documents / Number of documents with word t in it)

 

def test():
    ''' test your code thoroughly. put the testing cases here'''
    print('Pass')

def indexingCranfield():
    #ToDo: indexing the Cranfield dataset and save the index to a file
    # command line usage: "python index.py cran.all index_file"
    # the index is saved to index_file


     #filePath = sys.argv[1]
    #fileName = sys.argv[2]

    filePath = "CranfieldDataset/cran.all"
    fileName = "tempFile"
    invertedIndexer = InvertedIndex()
    data = CranFile(filePath)
    for doc in data.docs:
        invertedIndexer.indexDoc(doc)

    invertedIndexer.save(fileName)
    print(invertedIndexer.load(fileName))

if __name__ == '__main__':
    #test()
    indexingCranfield()


