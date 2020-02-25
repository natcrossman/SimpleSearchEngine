
'''
query processing

'''


"""Internal libraries"""
from util import Tokenizer
from cran import CranFile
from util import Tokenizer
from cranqry import loadCranQry
from index import Posting, InvertedIndex, IndexItem

"""Outside libraries"""
import json
import math
import sys
import os


class QueryProcessor:

    def __init__(self, query, index, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = InvertedIndex()
        self.index = self.index.loadData(index_file)
        # self.docs = collection
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
        
        document_ids.sort(key=len)
        results= document_ids[0]

        #checks if we only have 1 term in the query
        if len(document_ids) == 1:
            return results

        #checks if we have a term that does not appear in any of the documents
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

            
    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors
        
        #### postings should be a list of lists which contains word postings
        postings = [self.index.get_items_inverted()[w].get_posting_list() if w in self.index.get_items_inverted() else [] for w in self.processed_query ]

        ## either need to check if word is index first or modify index to return 0 if word is not in it
        idfs= [self.index.idf(w) for w in self.processed_query]

        document_ids = [k for d in postings for k in d]
        document_tfs = {d:[0]*len(self.processed_query) for d in document_ids}

        for inx, term in enumerate(postings):
            for document_id, posting in term.items():
                document_tfs[document_id][inx] = posting.term_freq()
        

        ## trivially easy since we now have a dictionary of documents that have tf vectors and we just multiply by idfs and then sort based on result
        return {}



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
