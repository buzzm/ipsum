import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.binary import Binary

import datetime
import base64
import sys
import json
import argparse

def main(args):
    parser = argparse.ArgumentParser(description=
"""Sort of like the real mongoimport but accepts more type information."""
   )
    parser.add_argument('importFile', metavar='importFile',
                   help='file containing JSON docs, CR delimited')
    parser.add_argument('-c','--collection', 
                   help='collection to import into')
    parser.add_argument('-d','--db', 
                        help="database to use")
    parser.add_argument('--host', default="localhost",
                        help="hostname to connect to")
    parser.add_argument('--port', type=int, default=27017,
                        help="port to connect to")

    parser.add_argument('--drop', 
                        action="store_true",
                        help="drop the collection first before importing into it")

    rargs = parser.parse_args()


    client = MongoClient(rargs.host, rargs.port)

    db = client[rargs.db]  # client["mydb"]
    coll = db[rargs.collection]
    
    if rargs.drop == True:
        coll.drop()  # start clean!
        
    filename = rargs.importFile
        
    with open(filename, 'r') as f:
        i = 0
        for line in f:
            i = i + 1
            #print "line", i
            m = json.loads(line)

            if "$comment" not in m:
                processMap(m)
                coll.insert(m)


def processThing(thing):
    newval = None

    if isinstance(thing, dict):
        cks = thing.keys()

        #  Sigh.... special case for $binary...
        if len(cks) == 2:
            ck1 = cks[0]
            ck2 = cks[1]

            if ck1 == "$binary" and ck2 == "$type":
                v = thing[ck1]
                q2 = base64.b64decode(v);
                q = Binary(q2)
                newval = q    

            if ck2 == "$binary" and ck1 == "$type":
                v = thing[ck2]
                q2 = base64.b64decode(v);
                q = Binary(q2)
                newval = q    

        elif len(cks) == 1:

            ck = cks[0]
            v = thing[ck]
            if ck == "$int":
                newval = int(v)
                
            elif ck == "$long":
                newval = long(v)
                
            elif ck == "$float":
                newval = float(v)
                
            elif ck == "$date":
                #q = datetime.datetime.utcfromtimestamp(v)
                #  Huh?!?  Can't create from timestamp with
                #  standard millis since epoch?!?  Pbbbb
                #q = datetime.datetime.fromtimestamp(v/1000)
                q = datetime.datetime.fromtimestamp(v)
                newval = q
                
            elif ck == "$binary":
                q2 = base64.b64decode(v);
                q = Binary(q2)
                newval = q    

            elif ck == "$oid":
                q = ObjectId(v)
                newval = q    


        if newval == None:
            processMap(thing)

    elif isinstance(thing, list):
        for i in range(0, len(thing)):
            v = thing[i]
            nv2 = processThing(v)
            if nv2 is not None:
                thing[i] = nv2

    return newval

                
def processMap(m):
    for k in m:
        item = m[k]
        
        newval = processThing(item)

        if newval is not None:
            m[k] = newval

#  Std way to fire it up....
main(sys.argv)
