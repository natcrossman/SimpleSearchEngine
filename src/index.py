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
import math
import json
import operator
import collections
import numpy as np
import os.path
from os import path
import pickle

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
    
    def get_docID(self):
        return self.__docID 

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
    #   @return        tf:int
    #   @exception     None
    ## 
    def term_freq(self):
      return  len(self.__positions)

    ##
    #   @brief         This method used for Json
    #   @param         self
    #   @return        (self.__docID, self.__positions)
    #   @exception     None
    ## 
    def get_info(self):
        return (self.__docID, self.__positions)
  

##
# @brief     Tested
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

    ##
    #   @brief         This method sets the posting list
    #   @param         self
    #   @return        None
    #   @exception     None
    ## 
    def set_posting_list(self, docID, posting):
        self.__posting[docID] = posting
    
    ##
    #   @brief         This method return the posting list
    #   @param         self
    #   @return        None
    #   @exception     None
    ## 
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
    #                  And also sort each posting positions
    # 
    #
    #   @param         self
    #   @return        sorted posting list and sorted dict posting list
    #   @exception     None
    ## 
    def return_sorted_posting(self):
        for key, postingTemp in self.__posting.items():
            postingTemp.sort()

        self.__sorted_postings    = sorted(self.__posting.items(), key=operator.itemgetter(0))
        self.__sorted_dict        = collections.OrderedDict(self.__sorted_postings)
        return self.__sorted_postings , self.__sorted_dict

    ##
    #   @brief         This method sort the posting list by document ID for more efficient merging. 
    #                  And also sort each posting positions.
    #     sort by document ID for more efficient merging. For each document also sort the positions
    #     Firt sort all posting positions
    #     then sort doc id 
    #     also creat new sorted dict. // not sure if need but why not
    # 
    #
    #   @param         self
    #   @return        Noe
    #   @exception     None
    ## 
    def sort(self):
        for key, postingTemp in self.__posting.items():
            postingTemp.sort()

        self.__sorted_postings    = sorted(self.__posting.items(), key=operator.itemgetter(0))
        self.__posting            = collections.OrderedDict(self.__sorted_postings)
    
    ##
    #   @brief         This Method transforms the postings data into a dictionary format to be converted to Json
    #   @param         self
    #   @return        posting: dict
    #   @exception     None
    ## 
    def posting_list_to_string(self):
        docID       = int
        positions   = []
        listOfShit  = {}
        posting  = {}
        numberOfTimeTermIsInDoc = 0
        for docID, post in  self.__posting.items():
            docID, positions = post.get_info()
            listOfShit[docID] = positions
            numberOfTimeTermIsInDoc += 1

        posting["df"]       = numberOfTimeTermIsInDoc 
        posting["posting"]  = listOfShit
        return posting
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
    #   @return        int
    #   @exception     None
    ## 
    def get_total_number_Doc(self):
        return self.__nDocs
    
    ##
    #   @brief     This method return the total number of doc in our data set
    #
    #   @param         self
    #   @param         Doc
    #   @return        items: dict
    #   @exception     None
    ## 
    def get_items_inverted(self):
        return self.__items

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
        newDoc              = doc.title +" "+   doc.author +" "+  doc.body
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
  
   

    ##
    #   @brief     This method sorts all indexing terms in our index 
    #
    #   @param         self
    #   @return        OrderedDict
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
    #   @param         term
    #   @return        postingList:dict
    #   @exception     None
    ## 
    def find(self, term):
        return self.__items[term]


    ##
    #   @brief     This method to dumper for json
    #
    #   @param         self
    #   @param         obj
    #   @return        toJSON or dict
    #   @exception     None
    ## 
    def dumper(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

    ##
    #   @brief     This method Serializes the inverted index to a json format and 
    #              clears the Memory that holds this dictionary
    #
    #   @param         self
    #   @param         filename
    #   @return        ValueError
    #   @exception     None
    ## 
    def save(self, filename):
        write_stream = open(filename, 'w')
        listTerm = self.sort_terms()
        dictMain = {}
        listInfo = {}

        for term, postingList in listTerm.items():
            dictTemp = postingList.posting_list_to_string()
            dictTemp["idf"] = self.idf(term)
            dictMain[term] = dictTemp

        listInfo["nDoc"] = self.get_total_number_Doc()
        listInfo["Data"] = dictMain
        try: 
            write_stream.write(json.dumps(listInfo, indent=3))
        except ValueError as e: 
             print ("Is not valid json")
        write_stream.close()

    ##
    #   @brief     This method deserializes a json file in a object by reallocating the self.__items
    #
    #   @param         self
    #   @param         filename
    #   @return        json: dict
    #   @exception     ValueError
    ## 
    def load(self, filename):
        try: 
            with open(filename) as json_file:
                return json.load(json_file)
        except ValueError as e: 
            print ("Is not valid json") 


    ##
    #   @brief     This method get IDF for  term by compute the inverted document frequency for a given term.
    #               We used this IDF = (Total number of (documents))/(Number of  (documents) containing the word)
    #
    #   @param         self
    #   @param         term
    #   @return        idf:int
    #   @exception     None
    ## 
    def idf(self, term):
        ''' '''
        if not term in self.__items:
            return 0
        termData = self.__items[term]
        N = self.get_total_number_Doc()
        df = len(termData.get_posting_list())
        idf = round(math.log10(N/(float(df))), 4)
        return idf
      
    ##
    #   @brief     This method create IDF for doc
    #
    #   @param         self
    #   @return        idf: {term: {docID:idf}}
    #   @exception     None
    ## 
    def idfDict(self):
        idf = collections.OrderedDict()
    
        for term, postingList in self.sort_terms().items():
            idf[term] = self.idf(term)

        return idf

    ##
    #   @brief     This method create TF for add doc
    #   There are different ways to represent TF we used tf = log(1+tf) 
    #   Another way is TF = (Frequency of the word in the sentence) / (Total number of words in the sentence)
    #   
    #   @param         self
    #   @return        word_tf_values: {term: {docID: tf, docID: tf }}  
    #   @exception     None
    ##   
    def tf_doc(self):
        word_tf_values = collections.OrderedDict()
        for term, postingList in self.sort_terms().items():
            doc_tf = collections.OrderedDict()
            for docID, post in postingList.get_posting_list().items():
                doc_tf[docID] = round(math.log10(1 + post.term_freq()), 4) #log normalize 
            word_tf_values[term] = doc_tf
        return word_tf_values

    ##
    #   @brief     This method create tfidf for all doc. 
    #              It structure is of the form {docID: {term: tf-idf,term: tf-idf }}    
    #   @param         self
    #   @param         word_tf_valuesm
    #   @param         idfDict    
    #   @return        TFIDF_dict:{docID: {term: tf-idf,term: tf-idf }}  
    #   @exception     None
    ##  
    def tf_idf(self,word_tf_valuesm, idfDict):
        TFIDF_dict =  collections.defaultdict(list)
        
        for term, postingList in self.sort_terms().items():
            tf_idf = 0.0 
            for doc , doctf in word_tf_valuesm[term].items():
                term_tf_idf_doc = {}
                tf_idf = doctf * idfDict[term]
                term_tf_idf_doc[term] = tf_idf
                TFIDF_dict[doc].append(term_tf_idf_doc)
        return TFIDF_dict  

    
        ##
    
    ##
    #   @brief     This method Saves the current state of the InvertedIndex
    #
    #   @param         self
    #   @param         filename
    #   @return        None
    #   @exception     AttributeError,  pickle.PickleError
    ##          
    def storeData(self, filename):
        
        try: 
            fileP = open(filename, "wb") 
            pickle.dump(self, fileP) # serialize class object
        except (AttributeError, pickle.PickleError):
            print("Error pickle.dump InvertedIndex ")
        fileP.close()
    
    ##
    #   @brief     This method Loads the saved InvertedIndex
    #
    #   @param         self
    #   @param         filename
    #   @return        invertedIndexer
    #   @exception     (pickle.UnpicklingError, ImportError, EOFError, IndexError, TypeError)
    ##  
    def loadData(self, filename): 
        try:
            fileP = open(filename ,"rb")
            invertedIndexer = pickle.load(fileP)
        except (pickle.UnpicklingError, ImportError, EOFError, IndexError, TypeError) as err:
            print(err)
            print("Error pickle.load InvertedIndex ")
        fileP.close()
        return invertedIndexer

##
#   @brief     This method Is used for tasting this Python script
#   Most testing was done in the debugger or ipython.  
# Small synthetic data sets were used and verified
#
#   @return        None
#   @exception     None
## 
def test():
    ''' test your code thoroughly. put the testing cases here'''
    dictTest_experiment = {'1': 3, '11': 1, '12': 1, '16': 1, '17': 1, '19': 1, '25': 1, '29': 1, '30': 2, '35': 1, '37': 1, '41': 1, '42': 1, '43': 1, '47': 1, '52': 2, '53': 1, '58': 1, '69': 1, '70': 1, '74': 2, '78': 2, '84': 3, '99': 2, '101': 1, '103': 1, '112': 1, '115': 1, '121': 1, '123': 3, '131': 1, '137': 1, '140': 1, '142': 1, '154': 1, '156': 1, '167': 1, '168': 1, '170': 1, '171': 2, '173': 2, '176': 1, '179': 2, '183': 1, '184': 1, '186': 3, '187': 1, '188': 1, '189': 2, '191': 1, '195': 3, '197': 2, '202': 1, '203': 1, '206': 2, '207': 2, 
    '212': 1, '216': 1, '220': 1, '222': 1, '225': 2, '227': 1, '230': 1, '234': 4, '245': 1, '251': 1, '256': 3, '257': 1, '262': 1, '271': 3, '273': 1, '277': 1, '282': 1, '283': 1, '286': 1, '287': 1, '289': 1, '294': 1, '295': 1, '304': 1, '307': 1, '329': 2, '330': 2, '334': 2, '338': 1, '339': 2, '344': 3, '345': 1, '346': 3, '347': 1, '354': 1, '360': 1, '369': 1, '370': 1, '372': 3, '377': 1, '397': 1, '409': 1, '411': 2, '413': 2, '418': 1, '420': 2, '421': 1, '423': 2, '427': 1, '433': 1, '435': 1, '439': 1, '441': 2, '442': 3, '443': 1, '453': 1, '455': 2, '462': 1, '464': 1, '467': 1, '484': 3, '494': 2, '496': 1, '497': 2, '498': 1, '501': 1, '503': 1, 
    '504': 1, '505': 1, '511': 1, '517': 1, '518': 2, '519': 1, '520': 2, '522': 3, '536': 1, '540': 1, '544': 3, '549': 2, '552': 2, '553': 1, '558': 2, '563': 1, '567': 1, '569': 2, '572': 4, '588': 1, '595': 1, '600': 1, '606': 1, '610': 1, '632': 1, '634': 1, '635': 1, '636': 1, '644': 1, '645': 1, '649': 1, '658': 1, '662': 2, '663': 2, '666': 2, '670': 1, '675': 1, '678': 1, '679': 1, '685': 3, '688': 4, '689': 2, '694': 1, '704': 2, '712': 1, '713': 1, '717': 1, '720': 1, '725': 1, '728': 1, '729': 1, '739': 1, '740': 1, '743': 1, '753': 1, '760': 3, '764': 1, '766': 4, '767': 3, '772': 3, '781': 2, '790': 1, '801': 3, '802': 1, '806': 1, '816': 2, '820': 1, 
    '823': 2, '825': 1, '827': 2, '829': 1, '830': 1, '836': 5, '844': 1, '845': 2, '846': 1, '847': 2, '856': 4, '857': 3, '858': 3, '863': 2, '866': 2, '867': 1, '869': 1, '878': 2, '881': 1, '887': 1, '891': 2, '907': 1, '911': 2, '912': 2, '923': 1, '924': 1, '927': 3, '928': 3, '932': 2, '935': 2, '946': 2, '950': 4, '951': 1, '954': 2, '955': 1, '959': 1, '961': 1, '964': 1, '965': 1, '973': 1, '974': 1, '984': 2, '986': 4, '996': 1, '997': 4, '999': 1, '1006': 1, '1008': 1, '1016': 1, '1019': 3, '1028': 1, '1039': 3, '1040': 1, '1045': 1, '1046': 1, '1049': 2, '1051': 1, '1062': 3, '1066': 4, '1069': 1, '1070': 1, '1074': 3, '1075': 3, '1076': 1, '1078': 1, '1080': 1, '1081': 1, '1082': 1, '1083': 1, '1092': 1, '1097': 3, '1098': 2, '1110': 1, '1112': 1, '1118': 2, '1122': 2, '1125': 1, '1127': 1, '1145': 1, '1146': 1, '1151': 1, '1153': 1, '1155': 2, '1156': 3, '1158': 1, '1159': 2, '1160': 2, '1161': 2, '1167': 2, '1171': 1, '1172': 1, '1177': 1, '1185': 1, '1186': 1, '1187': 1, '1192': 1, '1195': 1, '1196': 2, '1198': 1, '1199': 1, '1204': 3, '1205': 1, '1209': 3, '1212': 1, '1213': 2, '1214': 3, '1216': 1, '1218': 2, '1220': 1, '1222': 1, '1225': 3, '1227': 1, '1228': 1, '1230': 1, '1231': 1, '1234': 1, '1237': 1, '1261': 1, '1262': 1, '1263': 2, '1264': 2, '1268': 1, '1269': 2, '1277': 2, '1290': 1, '1298': 1, 
    '1302': 2, '1310': 1, '1314': 2, '1317': 1, '1319': 1, '1324': 1, '1337': 3, '1338': 2, '1339': 1, '1341': 1, '1352': 2, '1363': 2, '1364': 2, '1369': 1, '1372': 1, '1374': 1, '1378': 1, '1384': 1, '1390': 1, '1392': 1, '1396': 1, '1397': 1}
    dictTest_bifurc = {'957': 1, '1232': 1}

    filePath = "src/CranfieldDataset/cran.all"
    fileName = "src/Data/Test.json"
    fileNameO = "src/Data/TestPickle"        
    #filePath = "./CranfieldDataset/cran.all"
    #fileName = "./Data/tempFile.json"
    invertedIndexer = InvertedIndex()
    data = CranFile(filePath)
    for doc in data.docs:
        invertedIndexer.indexDoc(doc)

 
    
    #TF-IDF TEST
    TEMP = invertedIndexer.idf("experiment")
    Temp1 = invertedIndexer.idf("opportun")
    t = str(TEMP)
    t2 = str(Temp1)
    assert t == "0.6172"  ," Wrong idf."
    assert t2 == "2.8451" ," Wrong idf."

    assert len(invertedIndexer.find("experiment").get_posting_list()) == 338, "Worng Lenght for experiment term find does not work."
    assert invertedIndexer.get_total_number_Doc() == 1400, "Worng total nubmer of Doc in Corpus"
    

    for docID, post in invertedIndexer.find("experiment").get_posting_list().items():
        assert  docID in dictTest_experiment and post.term_freq() == dictTest_experiment[docID], "For Term experiment wrong value"
    
    dictTest_bifurc = {'957': 1, '1232': 1}
    for docID, post in invertedIndexer.find("bifurc").get_posting_list().items():
        assert  docID in dictTest_bifurc and post.term_freq() == dictTest_bifurc[docID], "For Term experiment wrong value"
    

    invertedIndexer.save(fileName)
    assert path.exists(fileName), "error in saving json data."

    invertedIndexer.storeData(fileNameO)
    assert path.exists(fileNameO), "error in saving json data."
    Temp = invertedIndexer.loadData(fileNameO)
    idfScore = Temp.invertedIndexer.idf("experiment")
    assert str(idfScore) == "0.6172"  ," Error in Load the picle file."

##
#   @brief     This method is the driver program for launching the Python script
#   @return        None
#   @exception     None
##  
def indexingCranfield():
    #ToDo: indexing the Cranfield dataset and save the index to a file
    # command line usage: "python index.py cran.all index_file"
    # the index is saved to index_file

    filePath = sys.argv[1]
    fileName = sys.argv[2]

    #filePath = "src/CranfieldDataset/cran.all"
    #fileName = "src/Data/tempFile"
    #filePath = "./CranfieldDataset/cran.all"
    #fileName = "./Data/tempFile"
   
    invertedIndexer = InvertedIndex()
    data = CranFile(filePath)
    for doc in data.docs:
        invertedIndexer.indexDoc(doc)

    invertedIndexer.storeData(fileName)
    print("Done")
   
#python index.py CranfieldDataset/cran.all Data/tempFile
if __name__ == '__main__':
    test()
    #indexingCranfield()
    


