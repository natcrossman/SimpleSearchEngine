Cranfield collection.
1398 abstracts (numbered 1 through 1400).
Aerodynamics.

Smallish collection, with large number of queries (225)

This directory contains:
-rw-rw-r--  1 chrisb   wheel        1446 Feb 14 18:30 README
        This file.
-rw-rw-r--  1 chrisb   wheel      592375 Feb 14 17:47 cran.all.Z
        Compressed version of document text.  Uncompressed version
        is 1644706 bytes
-rw-rw-r--  1 chrisb   wheel        6754 Feb 14 17:47 qrels.text.Z
        Relation giving relevance judgements.  Columns of file are
                query_id  doc_id   0    0
        to indicate doc_id is relevant to query_id.
        Uncompressed version:  21391
-rw-rw-r--  1 chrisb   wheel       12125 Feb 14 17:47 query.text.Z
        Text of queries.  Uncompressed: 28039
-rw-rw-r--  1 chrisb   wheel      559608 Feb 14 18:02 tf_doc.Z
        Indexed documents.  Columns of file are
             doc_id  0  concept_number  tf_weight  stemmed_word
        to indicate stemmed_word occurs in doc_id tf_weight times,
        and has been assigned the designator concept_number.
        Uncompressed: 2003724
-rw-rw-r--  1 chrisb   wheel       17226 Feb 14 17:50 tf_query.Z
        Indexed queries.   Columns of file are
             query_id  0  concept_number  tf_weight  stemmed_word
        to indicate stemmed_word occurs in query_id tf_weight times,
        and has been assigned the designator concept_number.
        Uncompressed: 28039

