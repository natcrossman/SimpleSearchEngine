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
from index import InvertedIndex
import doc
from cranqry import loadCranQry
from cran import CranFile
import random 
import sys
import os

import collections
from statistics import mean

#get avg NDCG values
def avg(listOfNDCG):
    return mean(listOfNDCG)

def readFile(fileName):
    fileObj = open(fileName, "r")
    lines = fileObj.readlines()
    return lines

# return a dict of qID and text
def getRandomQuery(queryFile,numberOfQueries):
    dictOfQueryID = {}
    dictQuery = random.sample(queryFile.items(), k=numberOfQueries)
    for queryTuple in dictQuery:
        dictOfQueryID[queryTuple[1].qid] = queryTuple[1].text

    return dictOfQueryID


def getResultsFrom_QrelsFile(listOfQueryRelsMaping,dictOfQuery):
    dictOfResult = collections.defaultdict(list)
    for query in listOfQueryRelsMaping:
        data = query.split()
        if data[0] in dictOfQuery:
            dictOfResult[data[0]].append(data[1]) 
    return dictOfResult

        
def eval():
    k               = 10 # k the number of top k pairs of (docID, similarity) to get from vectorQuery
    indexFile       = sys.argv[1]
    queryText       = sys.argv[2]
    qrelsText       = sys.argv[3]
    dictOfQuery     = {}
    dictQrelsText   = {}
    boolQueryDict   = {}
    vectorQueryDict = {}
    docCollection   = CranFile('src/CranfieldDataset/cran.all')
    NDCGScoreBool   = []
    numberOfQueries = sys.argv[4]
    NDCGScoreVector = []
    

    #Loads Files 
    listOfQueryRelsMaping   = readFile(qrelsText)
    queryFile   = loadCranQry(queryText)

    #Data Need
    dictOfQuery = getRandomQuery(queryFile,numberOfQueries)
    dictQrelsText =  getResultsFrom_QrelsFile(listOfQueryRelsMaping, dictOfQuery)



    #Loads queryFile and create dict of random N querys (dict = {Qid:text})
    

    #Load invertedIndexer Object from file Not sure if need?
    # invertedTempIndexer = InvertedIndex()
    # invertedIndexer = invertedTempIndexer.loadData(indexFile)

    for qid, queryText in dictOfQuery.items():
        queryProcessor = QueryProcessor(queryText,indexFile,docCollection.docs) # need 

        docIDs = queryProcessor.booleanQuery() # data would need to be like this [12, 14, 78, 141, 486, 746, 172, 573, 1003]
        boolQueryDict[qid] = docIDs

        dictOfDocIDAndSimilarity = queryProcessor.vectorQuery(k) # data need to look like k=3 [[625,0.8737006126353902],[401,0.8697643788341478],[943,0.8424991316663082]]
        vectorQueryDict[qid] = dictOfDocIDAndSimilarity

        #For Boolean part
        yTrue           = []
        yScore          = []
        for qID, listOfDocId in boolQueryDict.items():
            for docID in listOfDocId:
                yScore.append(1)
                if docID in dictQrelsText[qID]:
                    yTrue.append(1)
                else:
                    yTrue.append(0)
        #yScore.sort(reverse=True)    
        NDCGScoreBool.append(metrics.ndcg_score(yTrue[:10], yScore[:10], 10, "exponential"))


        #For Vector part
        yTrue           = []
        yScore          = []
        for qID, listOfDocId_and_score in vectorQueryDict.items():
            for docIdAndScore in listOfDocId_and_score:
                yScore.append(float(docIdAndScore[1]))
                if docID in dictQrelsText[qID]:
                     yTrue.append(1)
                else:
                     yTrue.append(0)
        #yScore.sort(reverse=True) 
        NDCGScoreVector.append(metrics.ndcg_score(yTrue[:10], yScore[:10], 10, "exponential"))

    vectorAvg = avg(NDCGScoreVector)
    BoolAvg = avg(NDCGScoreBool)

    PVALUETHING = stats.ttest_ind(BoolAvg,vectorAvg)

    #loop through vectorQueryDict add 0 or 1 to yScore and add 1 to yTrue
    #NDCG_Score = metrics.ndcg_score(yScore[:10], yTrue[:10], 10, "exponential")
    #once done looping and get score need to do avg numberOfQueries

    #loop through vectorQueryDict add 0 or 1 to yScore and add 1 to yTrue
    #NDCG_Score = metrics.ndcg_score(yScore[:10], yTrue[:10], 10, "exponential")
    #once done looping and get score need to do avg NDCGScoreVector

    print('Done')


if __name__ == '__main__':
    eval()

