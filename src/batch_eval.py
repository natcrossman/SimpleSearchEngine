'''
a program for evaluating the quality of search algorithms using the vector model

it runs over all queries in query.text and get the top 10 results,
and then qrels.text is used to compute the NDCG metric

usage:
    python batch_eval.py index_file query.text qrels.text n

    output is the average NDCG over all the queries for boolean model and vector model respectively.
	also compute the p-value of the two ranking results. 
'''
import metrics
import query
from scipy import stats
from query import QueryProcessor
from index import Posting, InvertedIndex, IndexItem
import doc
from cranqry import loadCranQry
from cran import CranFile
import random 
import sys
import os
import math
import collections
from statistics import mean
from timeit import default_timer as timer

##
#   @brief         This method return the Average for NDCGS values
#   @param         listOfNDCG
#   @return        None
#   @exception     None
## 
def avg(listOfNDCG):
    return mean(listOfNDCG)

##
#   @brief         This method reads a file and return a array
#   @param         fileName
#   @return        lines:list
#   @exception     None
## 
def readFile(fileName):
    fileObj = open(fileName, "r")
    lines = fileObj.readlines()
    return lines


##
#   @brief         This method generates a list of random queries to be an analyzed.
#                  The number of queries to be gotten is determined by the numberOfQueries value the user enters
#   @param         queryFile
#   @param         numberOfQueries
#   @return        dictOfQueryID: {qID:text,qID:text }
#   @exception     None
## 
def getRandomQuery(queryFile,numberOfQueries):
    dictOfQueryID = {}
    dictQuery = random.sample(queryFile.items(), k=numberOfQueries)
    for k, queryTuple in queryFile.items():
        dictOfQueryID[k] = queryTuple.text

    #return dictOfQueryID #{queryFile["226"].qid:queryFile["226"].text} #{queryFile["204"].qid:queryFile["204"].text} 
    return {queryFile["226"].qid:queryFile["226"].text} 

def getAllDataItems(queryFile):
    dictOfQueryID = {}
    for k, queryTuple in queryFile.items():
        dictOfQueryID[k] = queryTuple.text
    return dictOfQueryID 
##
#   @brief         This method gets the appropriate results for the randomly chosen queries.
#                  The outcome of this query is a dictionary of results used to compare our Querying process
#   @param         listOfQueryRelsMaping
#   @param         dictOfQuery
#   @return        dictOfResult: {qID:[DocID,DocID] }
#   @exception     None
## 
def getResultsFrom_QrelsFile(listOfQueryRelsMaping,dictOfQuery):
    dictOfResult = collections.defaultdict(list)
    for query in listOfQueryRelsMaping:
        data = query.split()
        if data[0] in dictOfQuery:
            dictOfResult[data[0]].append(data[1]) 
    return dictOfResult

##
#   @brief         Right now this method is used as the driver for the evaluation program.
#                  It initializes all necessary variables and calls all appropriate actions to get the results 
#                  of query and evaluation.
#
#   @return        None
#   @exception     None
#   @bug           This has not been Thoroughly tested yet. Only use synthetic data need your cope
##         
def eval():
    k               = 10 # k the number of top k pairs of (docID, similarity) to get from vectorQuery
    #indexFile       = sys.argv[1]v "src/Data/tempFile"
    indexFile       = "src/Data/tempFile"
    queryText       = 'src/CranfieldDataset/query.text'
    qrelsText       = 'src/CranfieldDataset/qrels.text'
    #queryText       = sys.argv[2]
    #qrelsText       = sys.argv[3]


    dictOfQuery     = {}
    dictQrelsText   = {}

    docCollection   = CranFile('src/CranfieldDataset/cran.all')
    NDCGScoreBool   = []
    #numberOfQueries = sys.argv[4]
    numberOfQueries = 220
    NDCGScoreVector = []
    

    #Loads Files 
    listOfQueryRelsMaping   = readFile(qrelsText)
    queryFile   = loadCranQry(queryText)

    #Data Need
    #dictOfQuery = getRandomQuery(queryFile,numberOfQueries)
    dictOfQuery = getAllDataItems(queryFile)
    dictQrelsText =  getResultsFrom_QrelsFile(listOfQueryRelsMaping, dictOfQuery)

    start = timer()
    queryProcessor = QueryProcessor("",indexFile,docCollection.docs) # This is an extremely expensive process\
    end = timer()
    print("Time for creating QueryProcessor:" , end - start) 
    countDoc = 0
    start = timer()
    for qid, queryText in dictOfQuery.items():
        countDoc +=1
        print("QID:",qid)
        start = timer()
        queryProcessor.loadQuery(queryText)
        end = timer()
        print("Time for Load:" , end - start) 
        print("qrels: ",dictQrelsText[qid])

        start = timer()
        docIDs = queryProcessor.booleanQuery() # data would need to be like this [12, 14, 78, 141, 486, 746, 172, 573, 1003]
        #docIDs_1 = queryProcessor.booleanQuery_1()
        end = timer()
        print("Time for booleanQuery:" , end - start) 

        
        start = timer()
        listOfDocIDAndSimilarity = queryProcessor.vectorQuery(k) # data need to look like k=3 [[625,0.8737006126353902],[401,0.8697643788341478],[943,0.8424991316663082]]
        #vectorQueryDict[qid] = dictOfDocIDAndSimilarity
        end = timer()
        print("Time for vectorQuery:", end - start) 
        print("booleanQuery:", docIDs)

        #For Boolean part
        start = timer()
        yTrue           = []
        yScore          = []
        for docID in docIDs:
            yScore.append(1)
            if docID in dictQrelsText[qid]:
                yTrue.append(1)
            else:
                yTrue.append(0)
        yTrue.sort(reverse=True)   
        score = metrics.ndcg_score(yTrue,yScore, 10, "exponential")
        if math.isnan(score):     
            NDCGScoreBool.append(0)
        else:
            NDCGScoreBool.append(score)
        end = timer()
        print("Time for  Boolean ndcg:", end - start) 

        #For Vector part
        start = timer()
        yTrue           = []
        yScore          = []
        print("vectorQuery:",listOfDocIDAndSimilarity)
        for docID_Score in listOfDocIDAndSimilarity:
            yScore.append(float(docID_Score[1]))
            if docID_Score[0] in dictQrelsText[qid]:
                    yTrue.append(1)
            else:
                    yTrue.append(0)
        yTrue.sort(reverse=True) 
        score = metrics.ndcg_score(yTrue,yScore, 10, "exponential")
        if math.isnan(score):     
            NDCGScoreVector.append(0)
        else:
            NDCGScoreVector.append(score)
        end = timer()
        print("Time for  Vector ndcg:", end - start) 

  
    vectorAvg = avg(NDCGScoreVector)
    BoolAvg = avg(NDCGScoreBool)
    print("Avg:", BoolAvg,vectorAvg)
    end = timer()
    print("\n\nTime for running ",countDoc ," queries:" , end - start) 

    p_va_ttest = stats.ttest_ind(NDCGScoreBool,NDCGScoreVector)
    p_va_wilcoxon = stats.wilcoxon(NDCGScoreBool,NDCGScoreVector)
    

    print("T-Test P-value: ",p_va_ttest)
    print("Wilcoxon P-value: ",p_va_wilcoxon)
    print('Done')

##
#   @brief         This is needed for testing
#
#   @return        None
#   @exception     None
#   @bug           
##  
def test():
    pass

if __name__ == '__main__':
    eval()

     # tf = posting.term_freq()
                # if tf > 0 :
                #     tf = 1 + math.log10(tf)
                # else:
                #     tf = 0
                # document_tfs[document_id][inx] = tf