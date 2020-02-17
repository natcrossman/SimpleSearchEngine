
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from norvig_spell import correction
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import doc

def isStopWord(word):
    ''' using the NLTK functions, return true/false'''
    # ToDo


def stemming(word):
    ''' return the stem, using a NLTK stemmer. check the project description for installing and using it'''


##
# @brief    This class is designed to take care of all text preprocessing for both indexing inquiry.  
#           please don't change the return types. 
#           You may add any message you need or modify the method for query indexing as desired but the 
#           base implementation should remain constant. 
#
#           
# @bug       None documented yet   
#
class Tokenizer:
    ##
    #   @brief         
    #   @note for doc indexing use before doc.title + " " + doc.body
    #   @param         self
    #   @param         doc
    #   @return        list_token list
    #   @exception     None
    ## 
    def tokenize_text(self, doc):
        list_token = []
        list_token = word_tokenize(doc)
        list_token = [t.lower() for t in list_token]
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
        return SnowballStemmer("english").stem(word)

    ##
    #   @brief      This method check to see if a word is a stopword. The Method returns True if the work 
    #               is a stopword.
    #   @param         self
    #   @param         word
    #   @return        boolean
    #   @exception     None
    ## 
    def isStopWord(self, word):
        ''' using the NLTK functions, return true/false'''
        setOfStopWords = set(stopwords.words('english'))
        if word not in setOfStopWords:
            return True
   
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
    #   @bug  The spell correction function doesn't necessarily seem to work as expected. 
    #           It changes even correctly spelled words.
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
        return self.stemming_list(self.remove_stopwords(self.spell_correction(self.tokenize_text(doc))))


