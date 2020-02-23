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


    #loop through vectorQueryDict add 0 or 1 to yScore and add 1 to yTrue
    #NDCG_Score = metrics.ndcg_score(yScore[:10], yTrue[:10], 10, "exponential")
    print('Done')


if __name__ == '__main__':
    #eval()
    queryFile = loadCranQry("src/CranfieldDataset/query.text")
    d =  getRandomQuery(queryFile,5)
    print(d)

{1: 1, 2: 2, 4: 3, 8: 4, 9: 5, 10: 6, 12: 7, 13: 8, 15: 9, 18: 10, 22: 11, 23: 12, 26: 13, 27: 14, 29: 15, 31: 16, 32: 17, 33: 18, 34: 19, 35: 20, 39: 21, 40: 22, 41: 23, 49: 24, 50: 25, 51: 26, 52: 27, 53: 28, 54: 29, 55: 30, 56: 31, 57: 32, 58: 33, 59: 34, 61: 35, 62: 36, 66: 37, 67: 38, 68: 39, 69: 40, 71: 41, 72: 42, 74: 43, 79: 44, 80: 45, 81: 46, 82: 47, 83: 48, 84: 49, 85: 50, 86: 51, 87: 52, 93: 53, 94: 54, 95: 55, 97: 56, 98: 57, 99: 58, 100: 59, 101: 60, 102: 61, 103: 62, 104: 63, 105: 64, 106: 65, 107: 66, 108: 67, 109: 68, 110: 69, 111: 70, 112: 71, 113: 72, 114: 73, 116: 74, 118: 75, 119: 76, 120: 77, 121: 78, 122: 79, 123: 80, 126: 81, 128: 82, 130: 83, 131: 84, 132: 85, 133: 86, 135: 87, 136: 88, 137: 89, 138: 90, 139: 91, 140: 92, 141: 93, 142: 94, 143: 95, 145: 96, 146: 97, 147: 98, 148: 99, 149: 100, 150: 101, 152: 102, 153: 103, 154: 104, 155: 105, 156: 106, 157: 107, 158: 108, 160: 109, 161: 110, 163: 111, 164: 112, 165: 113, 167: 114, 168: 115, 169: 116, 170: 117, 171: 118, 173: 119, 175: 120, 176: 121, 177: 122, 181: 123, 182: 124, 183: 125, 184: 126, 187: 127, 189: 128, 190: 129, 196: 130, 200: 131, 201: 132, 202: 133, 203: 134, 204: 135, 205: 136, 206: 137, 208: 138, 209: 139, 210: 140, 211: 141, 212: 142, 213: 143, 214: 144, 215: 145, 216: 146, 217: 147, 218: 148, 219: 149, 223: 150, 224: 151, 225: 152, 226: 153, 227: 154, 230: 155, 231: 156, 232: 157, 233: 158, 234: 159, 241: 160, 245: 161, 246: 162, 247: 163, 250: 164, 251: 165, 252: 166, 253: 167, 254: 168, 255: 169, 257: 170, 259: 171, 261: 172, 264: 173, 265: 174, 266: 175, 267: 176, 268: 177, 269: 178, 272: 179, 273: 180, 274: 181, 275: 182, 277: 183, 283: 184, 284: 185, 285: 186, 288: 187, 291: 188, 292: 189, 293: 190, 294: 191, 295: 192, 296: 193, 297: 194, 298: 195, 299: 196, 300: 197, 301: 198, 303: 199, 304: 200, 306: 201, 314: 202, 315: 203, 316: 204, 317: 205, 321: 206, 323: 207, 327: 208, 331: 209, 332: 210, 333: 211, 335: 212, 336: 213, 338: 214, 339: 215, 340: 216, 347: 217, 348: 218, 349: 219, 352: 220, 353: 221, 355: 222, 356: 223, 360: 224, 365: 225}