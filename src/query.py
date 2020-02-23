
'''
query processing

'''


"""Internal libraries"""
import doc
from util import Tokenizer
from cran import CranFile
from util import Tokenizer
from cranqry import loadCranQry

"""Outside libraries"""
import json
import math
import sys
import os


class QueryProcessor:

    def __init__(self, query, index, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = index
        self.docs = collection
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
            postings = [set(self.index[w]) for w in self.processed_query]
            postings.sort(key=len) # notice it is still smart to order by size 
            return reduce(set.intersection,postings) 
        '''
        with open(self.index) as json_file:
            dictData = json.load(json_file)


        #### This may need to change based on how index is implemented ####
        #### Postings should be a list of lists which contain only document ids ####
        postings = [self.index[w] for w in self.processed_query]
        postings.sort(key=len)
        results= postings[0]
        for p in postings[1:]:
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
        
        return results

            
    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors
        
        #### This may need to change based on how index is implemented ####
        #### Postings should be a list of lists which contains document ids and position ####
        postings = [self.index[w] for w in self.processed_query]
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
