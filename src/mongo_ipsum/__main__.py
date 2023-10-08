# -*- coding: utf-8 -*-
"""Hey, PyLint? SHUT UP"""
import argparse
import sys
import json
import requests
from pymongo import MongoClient
from mongo_ipsum import ipsum


def main() -> None:
    """Hey, PyLint? SHUT UP"""
    parser = argparse.ArgumentParser(description="Generate one or more \
                                     JSON objects containing random data \
                                     given a input json-schema.org compatible \
                                     schema specification")
    parser.add_argument('schemaFile', metavar='file',
                   help='json-schema.org schema file to use. could be a local file \
                    or a file hosted on a webserver')
    parser.add_argument('--count', default=1, type=int,
                   help='number of objects to create (default: 1)')
    parser.add_argument('--mode', choices=['pure','mongo','full'],
                        default="mongo",
                        help="""\
format of non-string data to emit.  pure is normal JSON; dates emitted
as ISO8601 strings and numbers are just numbers.   mongo is mongoDB-compatible
where dates are emitted as a special map {"$date", millis}.  mongoimport is
sensitive to maps with $ keys and will process the content as the indicated type.
full is a superset of mongoDB types.  Integers are emitted as {"$int", value},
floats as {"$float", value}.  mongoimport does not permit this -- but
pymonimport does.""")
    parser.add_argument('--defaultStringIpsum', choices=['word','sentence','paragraph','fname'],
                        default="word",
                        help="""\
default style of string to emit when presented with type:string.""")
    parser.add_argument('-c','--collection', default='test',
                        help='collection to import into')
    parser.add_argument('-d','--db', default='test',
                        help="database to use")
    parser.add_argument('--host', default="127.0.0.1",
                        help="hostname to connect to")
    parser.add_argument('--port', type=int, default=27017,
                        help="port to connect to")
    parser.add_argument('--drop',
                        action="store_true",
                        help="drop the collection first beofre importing into it")
    parser.add_argument('--upload',
                        action="store_true", default=False,
                        help="drop the collection first beofre importing into it")

    rargs = parser.parse_args()

    fname = rargs.schemaFile
    count = rargs.count

    if rargs.upload:
        client: any = MongoClient(rargs.host, rargs.port)

        db = client[rargs.db]
        coll = db[rargs.collection]

        if rargs.drop is True:
            coll.drop()  # start clean!
    # Retrive json schema from fname
    schema = {}
    try:
        if fname.startswith('http'):
            schema_req = requests.get(headers={'Content-type': 'application/json'},url = fname)
            if schema_req.status_code in [200,]:
                schema = schema_req.json()
        else:
            with open(fname, encoding='utf-8') as fp:
                schema = json.load(fp)
    except Exception as e:
        print(f"error loading data from '{fname}': {e}")
        sys.exit(1)

    if 'properties' not in schema:
        raise KeyError(f"Malformed json schema from {fname}")

    try:
        params = {
            "mode": rargs.mode,
            "defaultStringIpsum": rargs.defaultStringIpsum
            }

        q = ipsum.Ipsum(params)

        for _ in range(count):
            z: list = q.create_item(schema)
            print(json.dumps(z))
            if rargs.upload:
                coll.insert_one(z)

    except ValueError as e:
        print(f"error generating data from file '{fname}': {e}")
