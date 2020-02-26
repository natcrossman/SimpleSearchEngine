
'''
query processing

'''


"""Internal libraries"""
from util import Tokenizer
from cran import CranFile
from util import Tokenizer
from cranqry import loadCranQry
from index import Posting, InvertedIndex, IndexItem
from operator import itemgetter 
import math
from collections import Counter
"""Outside libraries"""
import json
import math
import sys
import os
import numpy as np

class QueryProcessor:
    ##
    # 
    #    @param         self
    #    @param         query
    #    @param         index
    #    @param         collection
    #    @return        None
    #    @brief         The constructor.  
    #                   This process is extremely expensive because it loads the entire pickle object into memory.
    #                   If we are only executing this for one query it is fine but if we are doing it 
    #                   for the evaluation used the load query instead
    #    @exception     None documented yet
    ##
    def __init__(self, query, index_file, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = InvertedIndex()
        self.index = self.index.loadData(index_file)
        self.docs = collection
        self.tokenizer = Tokenizer()
        if self.raw_query:
            self.processed_query = self.preprocessing(self.raw_query)

    
    ##
    #   @brief         This method is used to load the next query for evaluation
    #   @param         self
    #   @param         query
    #   @return        None
    #   @exception     None
    ## 
    def loadQuery(self,query):
        self.raw_query = query
        self.processed_query = self.preprocessing(self.raw_query)

    ##
    #   @brief         This method is used to load the next query for evaluation
    #   @param         self
    #   @param         raw_query
    #   @return        None
    #   @exception     None
    ## 
    def preprocessing(self,raw_query):
        ''' apply the same preprocessing steps used by indexing,
            also use the provided spelling corrector. Note that
            spelling corrector should be applied before stopword
            removal and stemming (why?)'''
        return self.tokenizer.transpose_document_tokenized_stemmed_spelling(raw_query)

    
    ##
    #   @brief         This method does the boolean query processing
    #   @param         self
    #   @return        results:list[docID]
    #   @bug           Fixed
    #   @exception     None
    ## 
    def booleanQuery(self):
        ''' boolean query processing; note that a query like "A B C" is transformed to "A AND B AND C" for retrieving posting lists and merge them'''
        ''' This method would likely be faster due to the use of  hashes, but I wanted to do what was shown in the slides
            from functools import reduce
            docs = [set(self.index[w]) for w in self.processed_query]
            docs.sort(key=len) # notice it is still smart to order by size 
            return reduce(set.intersection,docs) 
        '''

        ## checks that all of our query words are in the index, if not return [] ##
        for w in self.processed_query:
            if not w in self.index.get_items_inverted():
                return []

        ## checks if we only have 1 term in the query and returns its posting list if we do ##
        if len(self.processed_query) == 1:
            return list(self.index.get_items_inverted()[self.processed_query[0]].get_posting_list().keys())


        ### NCC change if a term in a quiry does not appear in our inverted index Forget/Discount term 
        #### document_ids is a list of lists containing only document ids ####
        document_ids = [list(self.index.get_items_inverted()[w].get_posting_list().keys()) for w in self.processed_query]

        # by sorting so that we start with the shortest list of documents we get a potential speed up
        document_ids.sort(key=len)
        results= document_ids[0]

        ## iterates through each query word and does the intersection of docids from its posting list with all those before it ##
        ## could be done faster if index was implemented as set or some other hash data structure
        for p in document_ids[1:]:
            intermediate=[]
            i,j = 0,0
            while i < len(results) and j < len(p): 
                if int(results[i]) < int(p[j]): 
                    i += 1
                elif int(results[i]) > int(p[j]): 
                    j+= 1
                else: 
                    intermediate.append(p[j]) 
                    j += 1
                    i += 1
            results = intermediate
            
            ## checks if we have already found terms totally disjoint from one another
            if len(results) == 0:
                return results

        return results


    #This works but not mine.. need to remove
    def __get__docIds(self, term):
            postings = self.__get__postings(term) 
            if postings is not None:
                return set([posting.get_docID() for _, posting in postings.items()])
            else:
                print("Warning: missing term {} in index.".format(term))
                # raise Exception("term not found!!")
                # pass
    def __get__postings(self, term):
        postings = None
        try:
            # if term in self.index.items:
            postings = self.index.get_items_inverted()[term].get_posting_list()
            # else:
            #     postings = self.index.items[correction(term)].posting
            #     print("spell corrected from {} to {}".format(term, correction(term)))
        except KeyError as e:
            print("Term {} not found in index.\nException: {}".format(term, e))
        return postings
    def booleanQuery_1(self):
        ''' boolean query processing; note that a query like "A B C" is transformed to "A AND B AND C" for retrieving posting lists and merge them'''
        # ToDo: return a list of docIDs
        q_tokens = self.processed_query
        common_docs = None
        for qtoken in q_tokens:
            try:
                if common_docs is None:
                    common_docs = self.__get__docIds(qtoken)
                else:
                    common_docs = common_docs.intersection(self.__get__docIds(qtoken))
            except Exception as e:
                print("error occured while querying, cause: ", e)
        ranked_results =  sorted(common_docs)
        
        return ranked_results


  

    ##
    #   @brief         This method compute cosine similarity for two vectors
    #   @param         self
    #   @param         vec1
    #   @param         vec2
    #   @return        score cosine: int
    #   @exception     None
    ## 
    def cosine_similarity(self,vec1,vec2):
        # "compute cosine similarity: (vec1*vec2)/(||vec1||*||vec2||)"
        AA, AB, BB = 0, 0, 0
        for i in range(len(vec1)):
            x = vec1[i]; y = vec2[i]
            AA += x*x
            BB += y*y    
            AB += x*y
        return AB/math.sqrt(AA*BB)
     
    ##
    #   @brief         This method compute vector model
    #   @param         self
    #   @param         k
    #   @return        cosines: dict{docID: score}
    #   @bug           Fixed
    #   @exception     None
    ## 
    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors
        
        query_words = list(set(self.processed_query))
        idfs= [self.index.idf(w) for w in query_words]

        # removes any words that have 0 idf as that means they didn't appear in the corpus, means save memory
        # probably not necessary to turn it into lists, and may actually be more appropriate to leave as tuples
        idfs,query_words = map(list,zip(*[i for i in list(zip(idfs,query_words)) if not i[0] == 0]))

        #Calculates tfs of relevant words
        query_term_counter = Counter(self.processed_query)
        query_tf_vector = [round(math.log10(query_term_counter[w]+1),4) for w in query_words] 

        ### NCC change if a term in a quiry does not appear in our inverted index Forget/Discount term 
        #### postings should be a list of lists which contains word postings

        postings = [self.index.get_items_inverted()[w].get_posting_list() for w in query_words if w in self.index.get_items_inverted() ]
      
        document_ids = set().union(*postings)
        document_tfs = {d:[0]*len(query_words) for d in document_ids}

        for inx, term in enumerate(postings):
            for document_id, posting in term.items():
                document_tfs[document_id][inx] = math.log10(posting.term_freq()+1)
       
        query_tfidf = np.multiply(query_tf_vector , idfs)

        cosines = Counter({d: self.cosine_similarity(query_tfidf,np.multiply(d_tf , idfs)) for d,d_tf in document_tfs.items() })

        return dict(sorted(cosines.items(), key = itemgetter(1), reverse = True)[:k])

    


#needed
def test():
    ''' test your code thoroughly. put the testing cases here'''

    ## BOOLEAN TESTS
    ## BTEST 1: 1 word query in index & no stopwords

    ## BTEST 2: 1 word query NOT in index & no stopwords

    ## BTEST 3: 1 word query of stopword

    ## BTEST 4: multiword query of in index & no stopwords & all unique

    ## BTEST 5: multiword query of NOT in index & no stopwords & all unique

    ## BTEST 6: multiword query of in index &  & NOT in index & no stopwords & all unique

    ## BTEST 7: multiword query ALL stopwords & all unique

    ## BTEST 8: multiword query of in index & stopwords & all unique

    ## BTEST 9: query consisting of NOT not in index & stopwords & all unique

    ## BTEST 10: multiword query of in index & NOT in index & stopwords & all unique

    ## BTEST 11: multiword query of in index & no stopwords & duplicates

    ## BTEST 12: multiword query of NOT in index & no stopwords & duplicates

    ## BTEST 13: multiword query of in index &  & NOT in index & no stopwords & duplicates

    ## BTEST 14: multiword query ALL stopwords & duplicates

    ## BTEST 15: multiword query of in index & stopwords & duplicates

    ## BTEST 16: query consisting of NOT in index & stopwords & dupicates

    ## BTEST 17: multiword query of in index & NOT in index & stopwords & duplicates


    ## VECTOR TESTS
    ## VTEST 1: 1 word query in index & no stopwords

    ## VTEST 2: 1 word query NOT in index & no stopwords

    ## VTEST 3: 1 word query of stopword

    ## VTEST 4: multiword query of in index & no stopwords & all unique

    ## VTEST 5: multiword query of NOT in index & no stopwords & all unique

    ## VTEST 6: multiword query of in index &  & NOT in index & no stopwords & all unique

    ## VTEST 7: multiword query ALL stopwords & all unique

    ## VTEST 8: multiword query of in index & stopwords & all unique

    ## VTEST 9: query consisting of NOT not in index & stopwords & all unique

    ## VTEST 10: multiword query of in index & NOT in index & stopwords & all unique

    ## VTEST 11: multiword query of in index & no stopwords & duplicates

    ## VTEST 12: multiword query of NOT in index & no stopwords & duplicates

    ## VTEST 13: multiword query of in index &  & NOT in index & no stopwords & duplicates

    ## VTEST 14: multiword query ALL stopwords & duplicates

    ## VTEST 15: multiword query of in index & stopwords & duplicates

    ## VTEST 16: query consisting of NOT in index & stopwords & dupicates

    ## VTEST 17: multiword query of in index & NOT in index & stopwords & duplicates


    print('Pass')

#needed
def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm"
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery
    # for booleanQuery, the program will print the total number of documents and the list of docuement IDs
    # for vectorQuery, the program will output the top 3 most similar documents

        
    indexFile       = "src/Data/tempFile"
    model_selection = "1"
    queryText       = 'src/CranfieldDataset/query.text'
    query_id        = "204"
    docCollection   = CranFile('src/CranfieldDataset/cran.all')
    #indexFile       = sys.argv[1]
    #model_selection = sys.argv[2]
    #queryText       = sys.argv[3]
    #query_id        = sys.argv[4]
    queryTest = ""
    queryFile   = loadCranQry(queryText)

    #Data Need
    queryTuple = queryFile[query_id]

    if query_id == queryTuple.qid:
        queryTest = queryTuple.text

    queryProcessor = QueryProcessor(queryTest,indexFile,docCollection.docs)
    if model_selection == "0":
        docIDs = queryProcessor.booleanQuery()
        print("Boolean")
        print("Total number of documents is:", str(len(docIDs)) + "\nThier DocIDs our:" + str(docIDs))

    elif model_selection == "1":
        print("Vector")
        print(queryProcessor.vectorQuery(3))


if __name__ == '__main__':
    #test()
    query()
