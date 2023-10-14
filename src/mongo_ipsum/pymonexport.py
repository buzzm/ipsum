# -*- coding: utf-8 -*-
"""Hey, PyLint? SHUT UP."""
import argparse
import base64
import datetime

from bson.binary import Binary
from bson.objectid import ObjectId
from pymongo import MongoClient

ARRAY_MODE = False

NO_ID = False

def main():
    """Hey, PyLint? SHUT UP."""
    global NO_ID

    parser = argparse.ArgumentParser(description="Sort of like the real mongoexport \
                                     but emits more type information. The \
                                     collection is dumped to stdout so redirect as needed"
                                    )
#    parser.add_argument('schemaFile', metavar='file',
#                   help='json-schema.org schema file to use')
    parser.add_argument('-c','--collection',
                   help='collection to dump')
    parser.add_argument('-d','--db',
                        help="database to use")
    parser.add_argument('--host', default="localhost",
                        help="hostname to connect to")
    parser.add_argument('--port', type=int, default=27017,
                        help="port to connect to")

    parser.add_argument('--noID',
                        action="store_true",
                        help="do not emit _id")

    rargs = parser.parse_args()

    try:
        client = MongoClient(rargs.host, rargs.port)

        db = client[rargs.db]  # client["mydb"]
        coll = db[rargs.collection]

        NO_ID = rargs.noID

        for c in coll.find():
            emit_doc(0, c)
            print("")

    except ValueError as e:
        print("fail of some kind: %s" % e)



def emit(spcs, strdata):
    print(strdata)
#     if arrayMode == True:
#         print(strdata)
#     else:
# #        print spcs, str,
#         print(strdata)
#        print "%s" % str,


def emit_item(lvl, ith, v):
    global NO_ID

    spcs = ""
    spcs2 = " " * ith

    if v is None:
        emit(spcs, "null")

    elif isinstance(v, Binary):
        q = base64.b64encode(v)
        emit(spcs,  "{\"$binary\":\"%s\", \"$type\":\"00\"}" % q )

    # elif isinstance(v, unicode):
    #     q = v.encode('ascii', 'replace')
    #     emit(spcs, "\"%s\"" % q)

    elif isinstance(v, str):
        emit(spcs, "\"%s\"" % v)

        # test for isinstance bool MUST precede test for int
        # because it will satisfy that condition too!
    elif isinstance(v, bool):
        # toString of bool works just fine...
        emit(spcs, f"{v}")

    elif isinstance(v, int):
        emit(spcs,  "{\"$int\":%s}" % v )

    elif isinstance(v, float):
        emit(spcs,  "{\"$double\":%s}" % v )

    # elif isinstance(v, long):
    #     emit(spcs,  "{\"$long\":%s}" % v )

    elif isinstance(v, datetime.datetime):
        q = v.strftime('%s')
        emit(spcs,  "{\"$date\":%s}" % q )

    elif isinstance(v, ObjectId):
        # toString of ObjectId mercifully does the right thing....
        emit(spcs,  "{\"$oid\":\"%s\"}" % v )


    elif isinstance(v, list):
        emit (spcs2,  "[" )
        i = 0
        for item in v:
            if i > 0:
                emit( spcs2, "," )

            emit_item(lvl + 1, i, item)
            i = i + 1

        emit( spcs2, "]" )

    elif isinstance(v, dict):
        emit_doc(lvl + 1, v)


    else:
        #  UNKNOWN type?
        t = type(v)
        emit(spcs,  "\"%s::%s\"" % (t,v) )



def emit_doc(lvl, m):
    if ARRAY_MODE is True:
        spcs = " " * (lvl*2)
    else:
        spcs = ""

    emit( spcs, "{")

    i = 0
    for k in m:
        if k == '_id' and NO_ID is True:
            continue

        item = m[k]
        if i > 0:
            emit(spcs,  ",\"%s\":" % (k) )
        else:
            emit(spcs,  "\"%s\":" % (k) )

        emit_item(lvl + 1, i, item)
        i = i + 1

    emit(spcs,  "}")

#  Std way to fire it up....
main()
