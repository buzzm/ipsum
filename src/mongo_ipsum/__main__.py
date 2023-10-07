# -*- coding: utf-8 -*-
"""Hey, PyLint? SHUT UP"""
import argparse
import json

from mongo_ipsum import ipsum


def main() -> None:
    """Hey, PyLint? SHUT UP"""
    parser = argparse.ArgumentParser(description="Generate one or more \
                                     JSON objects containing random data \
                                     given a input json-schema.org compatible \
                                     schema specification")
    parser.add_argument('schemaFile', metavar='file',
                   help='json-schema.org schema file to use')
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

    rargs = parser.parse_args()

    fname = rargs.schemaFile
    count = rargs.count
    with open(fname, encoding='utf-8') as fp:
        try:
            schema = json.load(fp)

            params = {
                "mode": rargs.mode,
                "defaultStringIpsum": rargs.defaultStringIpsum
                }

            q = ipsum.Ipsum(params)

            for _ in range(count):
                z: list = q.create_item(schema)
                print(json.dumps(z))

        except ValueError as e:
            print(f"error generating data from file '{fname}': {e}")

#  Std way to fire it up....
main()
