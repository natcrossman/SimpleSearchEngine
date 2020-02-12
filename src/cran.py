'''

processing the special format used by the Cranfield Dataset



'''
from doc import Document


class CranFile:
    def __init__(self, filename):
        self.docs = []

        cf = open(filename)
        docid = ''
        title = ''
        author = ''
        body = ''

        for line in cf:
            if '.I' in line:
                if docid != '':
                    body = buf
                    self.docs.append(Document(docid, title, author, body))
                # start a new document
                docid = line.strip().split()[1]
                buf = ''
            elif '.T' in line:
                None
            elif '.A' in line:
                title = buf # got title
                buf = ''
            elif '.B' in line:
                author = buf # got author
                buf = ''
            elif '.W' in line:
                buf = '' # skip affiliation
            else:
                buf += line
        self.docs.append(Document(docid, title, author, buf)) # the last one

if __name__ == '__main__':
    ''' testing '''

    cf = CranFile ('cran.all')
    for doc in cf.docs:
        print doc.docID, doc.title, doc.body
    print len(cf.docs)
