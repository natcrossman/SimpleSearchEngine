
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import doc

def isStopWord(word):
    ''' using the NLTK functions, return true/false'''

    # ToDo


def stemming(word):
    ''' return the stem, using a NLTK stemmer. check the project description for installing and using it'''

    # ToDo
#Here is an idea of a class, pls change or remove as you see fit. Cheers. 
class tokens:
    def token_for_doc(self, doc, type):
        list_token = []
        list_token = word_tokenize(doc.title + " " + doc.body)
        list_token = [t.lower() for t in list_token]
        return list_token

    def token_for_query(self, raw_query, type):
        list_token = []
        list_token = word_tokenize(raw_query)
        list_token = [t.lower() for t in list_token]
        return list_token
   
    def stemming(word):
        ''' return the stem, using a NLTK stemmer. check the project description for installing and using it'''
        return stemmer.stem(word)  

    def isStopWord(word):
        ''' using the NLTK functions, return true/false'''
        setOfStopWords = set(stopwords.words('stopwords'))
        if word in setOfStopWords:
            return True
        else: 
                return False