# -*- coding: utf-8 -*-
"Hey, PyLint? SHUT UP"
import argparse
import json

from pymongo import MongoClient

from mongo_ipsum import ipsum


def main() -> None:
    "Hey, PyLint? SHUT UP"
    parser = argparse.ArgumentParser(description="Given a input \
                                     json-schema.org compatible schema \
                                     specification, create one or more \
                                     entries in a mongoDB database of random data")
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


    client: any = MongoClient(rargs.host, rargs.port)

    db = client[rargs.db]  # client["mydb"]
    coll = db[rargs.collection]

    if rargs.drop is True:
        coll.drop()  # start clean!

    fname = rargs.schemaFile
    count = rargs.count

    with open(fname, encoding='utf-8') as fp:
        try:
            schema = json.load(fp)

            params = {
                "mode": "raw"
                }

            q = ipsum.Ipsum(params)

            for _ in range(count):
                z = q.create_item(schema)
                coll.insert(z)

        except ValueError as e:
            print(f"error generating data from file {fname}: {e}")



#  Std way to fire it up....
main()
