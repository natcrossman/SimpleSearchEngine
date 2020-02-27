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
def eval(testOn):
    k               = 10 # k the number of top k pairs of (docID, similarity) to get from vectorQuery
    dictQ_ID        = []
    indexFile       = sys.argv[1] #v "src/Data/tempFile"
    queryText       = sys.argv[2]
    qrelsText       = sys.argv[3]
    dictOfQuery     = {}
    dictQrelsText   = {}
    docCollection   = CranFile('CranfieldDataset/cran.all')
    NDCGScoreBool   = []
    numberOfQueries = int(sys.argv[4])
    NDCGScoreVector = []

    #indexFile       = "src/Data/tempFile"
    #queryText       = 'src/CranfieldDataset/query.text'
    #qrelsText       = 'src/CranfieldDataset/qrels.text'
    #numberOfQueries = 221
    
    #Loads Files 
    listOfQueryRelsMaping   = readFile(qrelsText)
    queryFile   = loadCranQry(queryText)

    #Data Need
    dictOfQuery = getRandomQuery(queryFile,numberOfQueries)
    if testOn:
       assert len(dictOfQuery) == numberOfQueries, "Error are getting random query"

    # Return all query     
    # dictOfQuery = getAllDataItems(queryFile)
    # if testOn:
    #     assert len(dictOfQuery) == 225, "Error are getting random query"

    dictQrelsText =  getResultsFrom_QrelsFile(listOfQueryRelsMaping, dictOfQuery)
    if testOn:
       assert len(dictQrelsText) == numberOfQueries, "Error number Of Queries to large"

    start = timer()
    queryProcessor = QueryProcessor("",indexFile,docCollection.docs) # This is an extremely expensive process\
    end = timer()
    if testOn:
        print("Time for creating QueryProcessor:" , end - start) 
    countDoc = 0
    start = timer()
    for qid, queryText in dictOfQuery.items():
        countDoc +=1
        dictQ_ID.append(qid)

        if testOn:
            print("QID:",qid)
        start = timer()
        queryProcessor.loadQuery(queryText)
        end = timer()
        if testOn:
            print("Time for Load:" , end - start) 
            print("qrels: ",dictQrelsText[qid])

        start = timer()
        docIDs = queryProcessor.booleanQuery() # data would need to be like this [12, 14, 78, 141, 486, 746, 172, 573, 1003]
        #docIDs_1 = queryProcessor.booleanQuery_1()
        end = timer()
        if testOn:
            print("Time for booleanQuery:" , end - start) 
        
        start = timer()
        listOfDocIDAndSimilarity = queryProcessor.vectorQuery(k) # data need to look like k=3 [[625,0.8737006126353902],[401,0.8697643788341478],[943,0.8424991316663082]]
        #vectorQueryDict[qid] = dictOfDocIDAndSimilarity
        end = timer()
        if testOn:
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
        if testOn:
            print("Time for  Boolean ndcg:", end - start) 

        #For Vector part
        start = timer()
        yTrue           = []
        yScore          = []
        if testOn:
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
        if testOn:
            print("Time for  Vector ndcg:", end - start) 

    if testOn:
        for QID, boolScore, vectorScore in zip(dictQ_ID, NDCGScoreBool,NDCGScoreVector):
            print("QID", QID, "Boolean Model:", boolScore,"Vector Model", vectorScore)

    print("\nQuerys Run:\n", dictQ_ID)
    print("\nThe Length Of Both NDCG Score is: ", len(NDCGScoreBool),"==",len(NDCGScoreVector))

    print('\nThe Avg NDCG Score')
    vectorAvg = avg(NDCGScoreVector)
    BoolAvg = avg(NDCGScoreBool)
    print("Avg NDCG Score for Bool:", BoolAvg, "\nAvg NDCG Score for Vector:",vectorAvg)
    end = timer()
    if testOn:
        print("\n\nTime for running ",countDoc ," queries:" , end - start) 
    
    print('\nThe P-Value')
    p_va_ttest = stats.ttest_ind(NDCGScoreBool,NDCGScoreVector)
    p_va_wilcoxon = stats.wilcoxon(NDCGScoreBool,NDCGScoreVector)
    print("T-Test P-value: ", p_va_ttest)
    print("Wilcoxon P-value: ", p_va_wilcoxon)
    print('Done')

##
# I manually tested 22 queries. 
# I created a small document  and queries and tested them to make sure system works rightly
# I compared my results to four other students
# Below is an example of test results and passing
# QID = 066  Query  =  "are there any theoretical methods for predicting base pressure"
#  Testing results:
#  Bool ['186', '283', '294', '522', '952', '1352']
#  [('952', 0.9899332313032174), ('294', 0.975691374849368), ('365', 0.9646073339833242), ('522', 0.9583289368881192), ('283', 0.9531819194740156), ('606', 0.9507909403809899), ('329', 0.9481591424735003), ('830', 0.9377375913195166), 
# ('947', 0.9295955325157395), ('564', 0.9248125671293725)]
#
# QID 112  Query = experimental results on hypersonic viscous interaction . 
# Bool ['25', '304', '329', '540', '572']
# vector [('540', 0.9769142340672038), ('572', 0.9747987666977254), ('25', 0.9738168255445173), 
# ('304', 0.9605645089312159), ('525', 0.940946870156558), ('305', 0.9350462305102516),
#  ('625', 0.9338542084077105), ('1395', 0.9305869355637617), ('63', 0.9303970912780767), 
# ('323', 0.9224028113813276)]
#
# QID 142 Query = what is the theoretical heat transfer rate at the stagnation point of a blunt body . 
# Bool ['84', '283', '329', '1104', '1393']
# vector [('540', 0.9769142340672038), ('572', 0.9747987666977254), ('25', 0.9738168255445173), 
# ('304', 0.9605645089312159), ('525', 0.940946870156558), ('305', 0.9350462305102516), 
# ('625', 0.9338542084077105), ('1395', 0.9305869355637617), ('63', 0.9303970912780767), 
# ('323', 0.9224028113813276)]
#
# QID 273  Query how does scale height vary with altitude in an atmosphere . 
# Bool ['548']
# vector [('548', 0.9686877096080251), ('617', 0.9237003752563703), ('616', 0.8480085077827825), 
# ('1324', 0.8322838916230021), ('622', 0.8225965994945199), ('1391', 0.8013511009161928), 
# ('1040', 0.740041371703577), ('1000', 0.7104424924454831), ('621', 0.7037552592541315), 
# ('799', 0.6873864734294)]
##

# python batch_eval.py Data/tempFile CranfieldDataset/query.text CranfieldDataset/qrels.text 100

if __name__ == '__main__':
    test_on = False
    eval(test_on)

