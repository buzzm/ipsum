# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient

import Ipsum

import json
import sys
import argparse


def main() -> None:
    "Hey, PyLint? SHUT UP"
    parser = argparse.ArgumentParser(description="Given a input json-schema.org compatible schema specification, create \
one or more entries in a mongoDB database of random data")
    parser.add_argument('schemaFile', metavar='file',
                   help='json-schema.org schema file to use')
    parser.add_argument('-c','--collection',
                   help='collection to import into')
    parser.add_argument('-d','--db',
                        help="database to use")
    parser.add_argument('--host', default="localhost",
                        help="hostname to connect to")
    parser.add_argument('--port', type=int, default=27017,
                        help="port to connect to")

    parser.add_argument('--count', default=1, type=int,
                   help='number of objects to create (default: 1)')
    parser.add_argument('--drop',
                        action="store_true",
                        help="drop the collection first beofre importing into it")

    rargs = parser.parse_args()


    client = MongoClient(rargs.host, rargs.port)

    db = client[rargs.db]  # client["mydb"]
    coll = db[rargs.collection]

    if rargs.drop == True:
        coll.drop()  # start clean!

    fname = rargs.schemaFile
    count = rargs.count
    fp = open(fname)

    try:
        schema = json.load(fp)

        params = {
            "mode": "raw"
            }

        q = Ipsum.Ipsum(params)

        for i in range(count):
            z = q.createItem(schema)
            coll.insert(z)

    except ValueError as e:
        print("error generating data from file \"%s\": %s" % (fname, e))



#  Std way to fire it up....
main()
