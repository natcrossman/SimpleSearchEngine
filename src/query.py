
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

    def __init__(self, query, index, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = InvertedIndex()
        self.index = self.index.loadData(index)
        #self.docs = collection
        self.tokenizer = Tokenizer()
        self.processed_query = self.preprocessing(self.raw_query)

    def preprocessing(self,raw_query):
        ''' apply the same preprocessing steps used by indexing,
            also use the provided spelling corrector. Note that
            spelling corrector should be applied before stopword
            removal and stemming (why?)'''
        return self.tokenizer.transpose_document_tokenized_stemmed_spelling(raw_query)

    def booleanQuery(self):
        ''' boolean query processing; note that a query like "A B C" is transformed to "A AND B AND C" for retrieving posting lists and merge them'''
        ''' This method would likely be faster due to the use of  hashes, but I wanted to do what was shown in the slides
            from functools import reduce
            docs = [set(self.index[w]) for w in self.processed_query]
            docs.sort(key=len) # notice it is still smart to order by size 
            return reduce(set.intersection,docs) 
        '''
        #### document_ids is a list of lists containing only document ids ####
        document_ids = [list(self.index.get_items_inverted()[w].get_posting_list().keys()) if w in self.index.get_items_inverted() else [] for w in self.processed_query ]
        
        # by sorting so that we start with the shortest list of documents we get a potential speed up
        document_ids.sort(key=len)
        results= document_ids[0]

        #checks if we only have 1 term in the query
        if len(self.processed_query) == 1:
            return results

        #checks if we have a term that does not appear in any of the documents, in which case we will not return any documents
        if len(results) == 0:
            return results

        for p in document_ids[1:]:
            intermediate=[]
            i,j = 0,0
            while i < len(results) and j < len(p): 
                if results[i] < p[j]: 
                    i += 1
                elif results[i] > p[j]: 
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

    # expects 2 vectors of equal length
    def cosine_similarity(self,vec1,vec2):
        # "compute cosine similarity: (vec1*vec2)/(||vec1||*||vec2||)"
        AA, AB, BB = 0, 0, 0
        for i in range(len(vec1)):
            x = vec1[i]; y = vec2[i]
            AA += x*x
            BB += y*y    
            AB += x*y
        return AB/math.sqrt(AA*BB)
            
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
        query_tf_vector = [math.log10(query_term_counter[w]+1) for w in query_words] 

        #### postings should be a list of lists which contains word postings
        postings = [self.index.get_items_inverted()[w].get_posting_list() if w in self.index.get_items_inverted() else dict() for w in query_words ]

        document_ids = set().union(*postings)
        document_tfs = {d:[0]*len(query_words) for d in document_ids}

        for inx, term in enumerate(postings):
            for document_id, posting in term.items():
                document_tfs[document_id][inx] = math.log10(posting.term_freq()+1)
        
        query_tfidf = np.multiply(query_tf_vector , idfs)

        cosines = Counter({d: self.cosine_similarity(query_tfidf,np.multiply(d_tf , idfs)) for d,d_tf in document_tfs.items() })

        return dict(sorted(cosines.items(), key = itemgetter(1), reverse = True)[:k])

    



def test():
    ''' test your code thoroughly. put the testing cases here'''
    print('Pass')

def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm"
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery
    # for booleanQuery, the program will print the total number of documents and the list of docuement IDs
    # for vectorQuery, the program will output the top 3 most similar documents


if __name__ == '__main__':
    #test()
    query()
