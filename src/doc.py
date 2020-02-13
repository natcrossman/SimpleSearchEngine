'''

The document class, containing information from the raw document and possibly other tasks

The collection class holds a set of docuemnts, indexed by docID

'''

class Document:
    def __init__(self, docid, title, author, body):
        self.docID = docid
        self.title = title
        self.author = author
        self.body = body


    # add more methods if needed


class Collection:
    ''' a collection of documents'''

    def __init__(self):
        self.docs = {} # documents are indexed by docID

    def find(self, docID):
        ''' 
        return a document object
        fixed to python 3.7
        '''
        key = self.docs.keys() 
        if docID in key:
            return self.docs[docID]
        else:
            return None

        # if self.docs.has_key(docID):
        #     return self.docs[docID]
        # else:
        #     return None


