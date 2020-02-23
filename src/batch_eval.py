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


        
def eval():
    k               = 10 # k the number of top k pairs of (docID, similarity) to get from vectorQuery
    yTrue           = []
    yScore          = []
    indexFile       = sys.argv[1]
    queryText       = sys.argv[2]
    qrelsText       = sys.argv[3]
    boolQueryDict   = {}
    vectorQueryDict = {}
    docCollection   = CranFile('src/CranfieldDataset/cran.all')
    NDCGScoreBool   = []
    numberOfQueries = sys.argv[4]
    NDCGScoreVector = []


    #Loads Files 
    listOfQueryRelsMaping   = readFile(qrelsText)
    listOFQuery             = readFile(queryText)

    #Loads queryFile and create dict of random N querys (dict = {Qid:text})
    queryFile   = loadCranQry(queryText)
    dictOfQuery = getRandomQuery(queryFile,numberOfQueries)

    #Load invertedIndexer Object from file Not sure if need?
    # invertedTempIndexer = InvertedIndex()
    # invertedIndexer = invertedTempIndexer.loadData(indexFile)
 
    for qid, queryText in dictOfQuery.items():
        queryProcessor = QueryProcessor(queryText,indexFile,docCollection.docs) # need 

        docIDs = queryProcessor.booleanQuery()
        boolQueryDict[qid] = docIDs

        dictOfDocIDAndSimilarity = queryProcessor.vectorQuery(k)
        vectorQueryDict[qid] = dictOfDocIDAndSimilarity


    #loop through vectorQueryDict add 0 or 1 to yScore and add 1 to yTrue
    #NDCG_Score = metrics.ndcg_score(yScore[:10], yTrue[:10], 10, "exponential")
    #once done looping and get score need to do avg numberOfQueries

    #loop through vectorQueryDict add 0 or 1 to yScore and add 1 to yTrue
    #NDCG_Score = metrics.ndcg_score(yScore[:10], yTrue[:10], 10, "exponential")
    #once done looping and get score need to do avg NDCGScoreVector

    print('Done')


if __name__ == '__main__':
    #eval()
    queryFile = loadCranQry("src/CranfieldDataset/query.text")
    d =  getRandomQuery(queryFile,5)
    print(d)
