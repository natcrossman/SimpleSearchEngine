
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from norvig_spell import correction
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import doc
import re
import string


from nltk.tokenize import RegexpTokenizer

##
# @brief    This class is designed to take care of all text preprocessing for both indexing inquiry.  
#           please don't change the return types. 
#           You may add any message you need or modify the method for query indexing as desired but the 
#           base implementation should remain constant. 
#           
# Could improve important performance by Optimizing removal of stopwords and stemming.. But not significant enough to query about
#           
# @bug       None documented yet   
#
class Tokenizer:

    def __init__(self, stopword_list=None, known_words={}):
        if stopword_list == None:
            self.stopword_list = set(stopwords.words('english'))
        else:
            self.stopword_list=stopword_list
        self.known_words=known_words
        self.stemmer = SnowballStemmer('english')

    ##
    #   @brief  
    # OHTER: Was tried.       
    # list_token_just = word_tokenize(doc)
    # list_token = list(filter(lambda list_token_just: list_token_just not in string.punctuation, list_token_just))
    # list_token = re.split(r"[\s-]+", doc)
    #   @note for doc indexing use before doc.title + " " + doc.body
    #   @param         self
    #   @param         doc
    #   @return        list_token list
    #   bug            fixed this was returning bad tokens
    #   @exception     None
    ## 
    def tokenize_text(self, doc):
        list_token = []
        tokenizer = RegexpTokenizer(r'\w+')
        list_token = tokenizer.tokenize(doc)
        list_token = list_token = [word.lower() for word in list_token] 
        return list_token
    
    ##
    #   @brief  This method is used for tokenizer queries. 
    #   The reason I created an extra method, that does the exact same thing as the previous tokenizer method,
    #   is for the small performance gain doing spell correction  inside this method gives me.
    #   Previously we called a separate method that took the completely tokenized list and then did spell correction on each term..
    #   This is not very good, O(n+M) 
    #   @note for doc indexing use before doc.title + " " + doc.body
    #   because of the limited size of our corpus, spelling correction results in slight boost
    #   with a larger corpus you would not do this, especially due to the simplicity of the spelling correction
    #   @param         self
    #   @param         doc
    #   @return        list_token list
    #   bug            fixed this was returning bad tokens
    #   @exception     None
    ## 
    def tokenize_text_for_q(self, doc):
        list_token = []
        tokenizer = RegexpTokenizer(r'\w+')
        list_token = tokenizer.tokenize(doc)
<<<<<<< HEAD
        list_token = [correction(word.lower()) if word not in self.known_words else word.lower() for word in list_token] 
=======
        # because of the limited size of our corpus, spelling correction results in slight boost
        # with a larger corpus you would not do this, especially due to the simplicity of the spelling correction
        list_token = list_token = [correction(word.lower()) if word not in self.known_words else word.lower() for word in list_token] 
>>>>>>> 914f01e5b3f112920bdbbb026919c269f70174e1
        return list_token

    ##
    #   @brief      This method return the stem worked using the SnowballStemmer NLTK stemmer. 
    #               We are using the SnowballStemmer as it is better than the original 'porter' stemmer.
    #               (e.i generously in SnowballStemmer = generous while generously in porter =gener)
    #
    #   @param         self
    #   @param         word
    #   @return        list_token list
    #   @exception     None
    ## 
    def stemming(self, word):
        return self.stemmer.stem(word)

    ##
    #   @brief      This method check to see if a word is a stopword. The Method returns True if the work 
    #               is not a stopword.
    #   @param         self
    #   @param         word
    #   @return        boolean
    #   @exception     None
    ## 
    def isStopWord(self, word):
        ''' using the list of stopwords from file, return true/false'''
        if word not in self.stopword_list:
            return True
        return False
   
    ##
    #   @brief  This method removes all stopwords from a tokenized list       
    #
    #   @param         self
    #   @param         list_token
    #   @return        list
    #   @exception     None
    ## 
    def remove_stopwords (self, list_token):
        temp=  [item for item in list_token if self.isStopWord(item)]
        return temp

    ##
    #   @brief   This method will properly stand in entire tokenized list       
    #
    #   @param         self
    #   @param         list_token
    #   @return        list
    #   @exception     None
    ## 
    def stemming_list(self, list_token):
        temp=  [self.stemming(item) for item in list_token]
        return temp

    ##
    #   @brief   This method will spell correct all token words
    #   @bug     The spell correction function doesn't necessarily seem to work as expected. 
    #            It changes even correctly spelled words. Best results seem to come from using the 
    #            dictionary as the base text for the spoke correction algorithm. 
    #            Tried other documents with no bettering success.
    #
    #   @param         self
    #   @param         list_token
    #   @return        list 
    #   @exception     None
    ## 
    def spell_correction(self, list_token):
        temp=  [correction(item) for item in list_token]
        return temp
       
# Technically all above methods could be private

    ##
    #   @brief   This method receives a document and turns each word into a token.
    #             These tokens then ran through a stemming algorithm.   
    #    
    # NOTE: This method is only used in the Index class.     
    #
    #   @param         self
    #   @param         doc
    #   @return        list
    #   @exception     None
    ## 
    def transpose_document_tokenized_stemmed(self, doc):
        return self.stemming_list(self.remove_stopwords(self.tokenize_text(doc)))
        
    ##
    #   @brief   This method receives a document and turns each word into a token, 
    #            fixes spelling mistakes, remove stopwords, performs stemming.
    # NOTE: This method is only used in the query class.     
    #  
    #   @param         self
    #   @param         doc
    #   @return        list        
    #   @exception     None
    ## 
    def transpose_document_tokenized_stemmed_spelling(self, doc):
        return self.stemming_list(self.remove_stopwords(self.tokenize_text_for_q(doc)))


