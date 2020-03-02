
'''
query processing

'''


"""Internal libraries"""
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
import random
from timeit import default_timer as timer

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
        self.tokenizer = Tokenizer(known_words=set(self.index.get_items_inverted().keys()))
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
        if len(self.processed_query) == 0:
            return[]

        ## checks that all of our query words are in the index, if not return [] ##
        for w in self.processed_query:
            if not w in self.index.get_items_inverted():
                return []

        ## checks if we only have 1 term in the query and returns its posting list if we do ##
        if len(self.processed_query) == 1:
            return list(self.index.get_items_inverted()[self.processed_query[0]].get_posting_list().keys())

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
        return round(AB/math.sqrt(AA*BB),4)
     
    ##
    #   @brief         This method compute vector model
    #   @param         self
    #   @param         k
    #   @return        cosines: dict{docID: score}
    #   @bug           Fixed
    #   @exception     ValueError
    ## 
    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors
        if len(self.processed_query) == 0:
            all_docids = set()
            for _,v in self.index.get_items_inverted().items():
                all_docids.update(v.get_posting_list().keys())
            return [(str(id),0) for id in sorted(list(map(int,all_docids)))[:k]]

        query_words = list(set(self.processed_query))
        idfs= [self.index.idf(w) for w in query_words]

        # undefined behavior from document on what to do if k is larger than the corpus
        try:
            if k > self.index.get_total_number_Doc():
                raise ValueError('k is greater than number of documents') 
        except ValueError as err:
            print(err.args)
            return 

        # below we define behavior if none of the words in the query are in any documents
        # this behavior was not defined in instructions so no documents seems most appropriate
        # if you used google and got 0 cosine it would return 0 documents even if you wanted the 50 most relevant
        if set(idfs) == {0}: 
            all_docids = set()
            for _,v in self.index.get_items_inverted().items():
                all_docids.update(v.get_posting_list().keys())
            return [(str(id),0) for id in sorted(list(map(int,all_docids)))[:k]]

        # removes any words that have 0 idf as that means they didn't appear in the corpus, means save memory
        # probably not necessary to turn it into lists, and may actually be more appropriate to leave as tuples
        idfs,query_words = map(list,zip(*[i for i in list(zip(idfs,query_words)) if not i[0] == 0]))

        #Calculates tfs of relevant words
        query_term_counter = Counter(self.processed_query)
        query_tf_vector = [round(math.log10(query_term_counter[w]+1),4) for w in query_words] 

        #Other way of doing tf
        #query_tf_vector = [round(1 + math.log10(query_term_counter[w]),4) if query_term_counter[w] > 0 else 0 for w in query_words]
    


        ### NCC change if a term in a quiry does not appear in our inverted index Forget/Discount term 
        #### postings should be a list of lists which contains word postings

        postings = [self.index.get_items_inverted()[w].get_posting_list() for w in query_words if w in self.index.get_items_inverted() ]
      
        document_ids = set().union(*postings)
        document_tfs = {d:[0]*len(query_words) for d in document_ids}

        for inx, term in enumerate(postings):
            for document_id, posting in term.items():
                #log normalization
                document_tfs[document_id][inx] = math.log10(posting.term_freq()+1)
                
                #Other
                # tf = posting.term_freq()
                # if tf > 0 :
                #     tf = 1 + math.log10(tf)
                # else:
                #     tf = 0
                # document_tfs[document_id][inx] = tf

        query_tfidf = np.multiply(query_tf_vector , idfs)

        cosines = Counter({d: self.cosine_similarity(query_tfidf,np.multiply(d_tf , idfs)) for d,d_tf in document_tfs.items() })
        # this has to be a list as dict are not sorted...
        # need a consistent ordering of documents when multiple documents have the same score we first sort on score then docid, very slow 
        # if we know k or know the number of documents we could use numpy to preallocate memory which means we would not have to use append and could just use copy
        temp_k = k
        scores = sorted(list(set(cosines.values())),reverse=True)
        ret = []
        for s in scores:
            docs_with_score_s = sorted([int(d) for d,v in cosines.items() if v == s])
            if len(docs_with_score_s) >= temp_k:
                docs_with_score_s = docs_with_score_s[:temp_k]
                ret.extend([(str(d),s) for d in docs_with_score_s])
                temp_k=0
                break
            else:
                temp_k = temp_k-len(docs_with_score_s)
                ret.extend([(str(d),s) for d in docs_with_score_s])
        if not temp_k == 0:
            all_docids = set()
            for _,v in self.index.get_items_inverted().items():
                all_docids.update(v.get_posting_list().keys())

            ret.extend([(str(j),0) for j in sorted(list(map(int,all_docids.difference({i[0] for i in ret}))))[:temp_k]])
        return ret

    


#needed
def test():
    ''' test your code thoroughly. put the testing cases here'''

    # indexFile       = "src/Data/tempFile"
    indexFile       = "./Data/tempFile"

    qp = QueryProcessor('',indexFile,None)

   
    print("Preprocessing Tests")

    ## PREPROCESSING TESTS ##
    ptest_queries=[        
        "box",
        "boxc",
        "experi",
        "experiment"]
    # control for misspelled "box"
    qp.loadQuery(ptest_queries[0])
    spell_control = qp.booleanQuery()

    # ## PTEST 1: misspelled word "boxc", unfortunately the spelling corrector is so simple there were few examples that would work with it
    qp.loadQuery(ptest_queries[1])
    assert spell_control == qp.booleanQuery()

    ## control for stem "experi"
    qp.loadQuery(ptest_queries[2])
    stem_control = qp.booleanQuery()

    ## PTEST 2: word stemming "experiment"
    qp.loadQuery(ptest_queries[3])
    assert stem_control == qp.booleanQuery()
    print("Preprocessing Tests: PASSED")
    print()

    print("Boolean Tests")
    ## BOOLEAN TESTS
    btest_queries=[
        "bifurc",
        "doooooog",
        "the",
        "downwash investig experi",
        "doooooog cat",
        "bifurc doooooog",
        "the in",
        "downwash experi investig in the of",
        "dooooooog the",
        "experi dooooooog the",
        "investig downwash downwash downwash experi experi",
        "doooooog doooooog cat cat",
        "the the the the the the of of of",
        "investig experi experi doooooog doooooog",
        "investig downwash experi experi the the the",
        "the doooooog the cat the rhino",
        "the experi doooooog investig of the cat",
        "investig investig investig investig investig investig investig investig investig investig investig investig investig investig experiment",
    ]
    ## BTEST 1: 1 word query in index & no stopwords
    qp.loadQuery(btest_queries[0])
    assert len({'957','1232'}.difference(set(qp.booleanQuery()))) == 0

    ## BTEST 2: 1 word query NOT in index & no stopwords
    qp.loadQuery(btest_queries[1])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 3: 1 word query of stopword
    qp.loadQuery(btest_queries[2])
    assert len(qp.booleanQuery()) == 0 and len(qp.processed_query) == 0

    ## BTEST 4: multiword query of in index & no stopwords & all unique
    qp.loadQuery(btest_queries[3])
    res = (qp.booleanQuery())
    assert len(res)==1 and '1166' in res

    ## BTEST 5: multiword query of NOT in index & no stopwords & all unique
    qp.loadQuery(btest_queries[4])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 6: multiword query of in index & NOT in index & no stopwords & all unique
    qp.loadQuery(btest_queries[5])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 7: multiword query ALL stopwords & all unique
    qp.loadQuery(btest_queries[6])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 8: multiword query of in index & stopwords & all unique
    qp.loadQuery(btest_queries[7])
    res = qp.booleanQuery()
    assert len(res)==1 and '1166' in res

    ## BTEST 9: query consisting of NOT in index & stopwords & all unique
    qp.loadQuery(btest_queries[8])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 10: multiword query of in index & NOT in index & stopwords & all unique
    qp.loadQuery(btest_queries[9])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 11: multiword query of in index & no stopwords & duplicates
    qp.loadQuery(btest_queries[10])
    res = (qp.booleanQuery())
    assert len(res)==1 and '1166' in res

    ## BTEST 12: multiword query of NOT in index & no stopwords & duplicates
    qp.loadQuery(btest_queries[11])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 13: multiword query ALL stopwords & duplicates
    qp.loadQuery(btest_queries[12])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 14: multiword query of in index & NOT in index & no stopwords & duplicates
    qp.loadQuery(btest_queries[13])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 15: multiword query of in index & stopwords & duplicates
    qp.loadQuery(btest_queries[14])
    assert len(res)==1 and '1166' in res

    ## BTEST 16: query consisting of NOT in index & stopwords & dupicates
    qp.loadQuery(btest_queries[15])
    assert len(qp.booleanQuery()) == 0

    ## BTEST 17: multiword query of in index & NOT in index & stopwords & duplicates
    qp.loadQuery(btest_queries[16])
    assert len(qp.booleanQuery()) == 0

    print("Boolean Tests: PASSED")
    print()

    ## VECTOR TESTS
    print("Vector Tests")
    vtest_queries=[
        "bifurc",
        "doooooog",
        "the",
        "downwash investig experi",
        "doooooog cat",
        "bifurc doooooog",
        "the in",
        "downwash experi investig in the of cat doooooog",
        "investig investig downwash experi",
        "investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig investig downwash experiment",
    ]
    ## VTEST 1: 1 word query in index & no stopwords
    qp.loadQuery(vtest_queries[0])
    vtest1 = qp.vectorQuery(3)
    assert len(vtest1) == 3 and vtest1[0][1] == 1 and vtest1[1][1] == 1 and vtest1[2][1] == 0

    ## VTEST 2: 1 word query NOT in index & no stopwords
    qp.loadQuery(vtest_queries[1])
    vtest2 = qp.vectorQuery(3)
    assert vtest2[0][0] == '1' and vtest2[1][0] == '2' and vtest2[2][0] == '3' and len(vtest2)==3 and vtest2[0][1]+vtest2[1][1]+vtest2[2][1] == 0

    ## VTEST 3: 1 word query of stopword
    qp.loadQuery(vtest_queries[2])
    vtest3 = qp.vectorQuery(3)
    assert vtest3[0][0] == '1' and vtest3[1][0] == '2' and vtest3[2][0] == '3' and len(vtest3)==3 and vtest3[0][1]+vtest3[1][1]+vtest3[2][1] == 0

    ## VTEST 4: multiword query of in index & no stopwords & all unique
    qp.loadQuery(vtest_queries[3])
    vtest4 = qp.vectorQuery(3)
    assert len(vtest4) == 3 and vtest4[0][0]=='1166' and vtest4[0][1] == .9763 and vtest4[1][0]=='704' and vtest4[1][1]==.9378 and vtest4[2][0]=='894' and vtest4[2][1]==.8952

    ## VTEST 5: multiword query of NOT in index & no stopwords & all unique
    qp.loadQuery(vtest_queries[4])
    vtest5 = qp.vectorQuery(3)
    assert vtest5[0][0] == '1' and vtest5[1][0] == '2' and vtest5[2][0] == '3' and len(vtest5)==3 and vtest5[0][1]+vtest5[1][1]+vtest5[2][1] == 0

    ## VTEST 6: multiword query of in index &  & NOT in index & no stopwords & all unique
    qp.loadQuery(vtest_queries[5])
    vtest6 = qp.vectorQuery(3)
    assert vtest1 == vtest6

    ## VTEST 7: multiword query ALL stopwords & all unique
    qp.loadQuery(vtest_queries[6])
    vtest7 = qp.vectorQuery(3)
    assert vtest7[0][0] == '1' and vtest7[1][0] == '2' and vtest7[2][0] == '3' and len(vtest7)==3 and vtest7[0][1]+vtest7[1][1]+vtest7[2][1] == 0

    ## VTEST 8: multiword query of in index & stopwords & all unique
    qp.loadQuery(vtest_queries[7])
    vtest8 = qp.vectorQuery(3)
    assert vtest4 == vtest8

    ## VTEST 9: multiword query of in index & no stopwords & duplicates
    qp.loadQuery(vtest_queries[8])
    vtest9 = qp.vectorQuery(3)
    assert len(vtest9) == 3 and vtest9[0][0]=='1166' and vtest9[0][1] == .9704 and vtest9[1][0]=='673' and vtest9[1][1]==.9036 and vtest9[2][0]=='894' and vtest9[2][1]==.8948


    ## VTEST 10: multiword query to check the correctness of tfidf calculation
    qp.loadQuery(vtest_queries[9])
    vtest10 = qp.vectorQuery(3)
    assert not vtest10 == vtest9 and not vtest10[1][1] == 704
    print("Vector Tests: PASSED")

#needed
def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm"
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery
    # for booleanQuery, the program will print the total number of documents and the list of docuement IDs
    # for vectorQuery, the program will output the top 3 most similar documents
        
    #ndexFile       = "src/Data/tempFile"
    #model_selection = "0"
    #queryText       = 'src/CranfieldDataset/query.text'
    #query_id        = "226"
    docCollection   = CranFile('CranfieldDataset/cran.all')
    indexFile       = sys.argv[1]
    model_selection = sys.argv[2]
    queryText       = sys.argv[3]
    query_id        = sys.argv[4]
    query_id        =  str(query_id).zfill(3) # need for number 001 or 050
    queryTest = ""
    queryFile   = loadCranQry(queryText)

    #Data Need
    if not model_selection == '2':
        queryTuple = queryFile[query_id]

        if query_id == queryTuple.qid:
            queryTest = queryTuple.text

    queryProcessor = QueryProcessor(queryTest,indexFile,docCollection.docs)
    if model_selection == "0":
        docIDs = queryProcessor.booleanQuery()
        print("Boolean")
        print("Total number of documents is:", str(len(docIDs)) + "\nTheir DocIDs our:" + str(docIDs))

    elif model_selection == "1":
        print("Vector")
        print(queryProcessor.vectorQuery(3))

    elif model_selection == "2":
        numberOfTimeToLoop  = 5
        numberOfQueries = int(query_id)
        k = 10
        bresults=[]
        vresults=[]
        #Data Need
        for _ in range(numberOfTimeToLoop):
            #get list of Query result from qrel.txt
            
            dictOfQuery = getRandomQuery(queryFile,numberOfQueries)
            queryProcessor = QueryProcessor("",indexFile,docCollection.docs) # This is an extremely expensive process\
            
            start = timer()
            for __, queryText in dictOfQuery.items():
                queryProcessor.loadQuery(queryText)
                #docIDs = queryProcessor.booleanQuery()
                queryProcessor.booleanQuery()
            end = timer()    
 #           print("Run:",i+1, "\nTime for boolean model on Query (",numberOfQueries,") \nTime:", end - start, "\n") 
            bresults.append(end-start)
            start = timer()
            for __, queryText in dictOfQuery.items():    
                #listOfDocIDAndSimilarity = queryProcessor.vectorQuery(k)
                queryProcessor.vectorQuery(k)
            end = timer()
#            print("Run:",i+1, "\nTime for Vector model on Query (",numberOfQueries,") \nTime:", end - start, "\n") 
            vresults.append(end-start)

            
        print("Model\t\tRun:"+'\t\t\tRun:'.join(map(str,range(numberOfTimeToLoop+1)[1:])))
        print()
        print("Boolean Model: \t"+'\t'.join(map(str,bresults)))
        print()
        print("Vector Model: \t"+'\t'.join(map(str,vresults)))
        print()
               




##
#   @brief         This method generates a list of random queries to be an analyzed.
#                  The number of queries to be gotten is determined by the numberOfQueries value the user enters
#   @param         queryFile
#   @param         numberOfQueries
#   @return        dictOfQueryID: {qID:text,qID:text }
#   @exception     None
## 
def getRandomQuery(queryFile,numberOfQueries):
    assert numberOfQueries < 222, "Error number Of Queries to large"

    dictOfQueryID = {}
    dictQuery = random.sample(queryFile.items(), k=numberOfQueries)
    for queryTuple in dictQuery:
        dictOfQueryID[queryTuple[1].qid] = queryTuple[1].text

    return dictOfQueryID #{queryFile["226"].qid:queryFile["226"].text} #{queryFile["204"].qid:queryFile["204"].text} 
    #return {queryFile["273"].qid:queryFile["273"].text} 

def getAllDataItems(queryFile):
    dictOfQueryID = {}
    for k, queryTuple in queryFile.items():
        dictOfQueryID[k] = queryTuple.text
    return dictOfQueryID 


#Running python query.py Data/tempFile 0 CranfieldDataset/query.text 226
if __name__ == '__main__':
    #test()
    query()
