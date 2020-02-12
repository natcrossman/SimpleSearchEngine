
'''
  handling the specific input format of the query.text for the Cranfield data
'''


class CranQry:
    def __init__(self, qid, text):
        self.qid = qid
        self.text = text

def loadCranQry(qfile):
    queries = {}
    f = open(qfile)
    text = ''
    qid = ''
    for line in f:
        if '.I' in line:
            if qid !='':
                queries[qid] = CranQry(qid, text)
                #print 'qid:', qid, text
            qid = line.strip().split()[1]
            text = ''
        elif '.W' in line:
            None
        else:
            text += line
    queries[qid] = CranQry(qid, text)
    return queries

def test():
    '''testing'''
    qrys =  loadCranQry('query.text')
    for q in qrys:
        print q, qrys[q].text
    print len(qrys)

if __name__ == '__main__':
    test()
