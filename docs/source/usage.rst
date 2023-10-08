Usage
=====

Installation
-------------

From sources
^^^^^^^^^^^^^

.. code-block:: console

    (.venv) $ pip install .

Get help
--------

.. code-block:: console

    (.venv) $ mongo_ipsum --help
    usage: mongo_ipsum [-h] [--count COUNT] [--mode {pure,mongo,full}] [--defaultStringIpsum {word,sentence,paragraph,fname}] [-c COLLECTION] [-d DB] [--host HOST] [--port PORT] [--drop] [--upload] file

    Generate one or more JSON objects containing random data given a input json-schema.org compatible schema specification

    positional arguments:
    file                  json-schema.org schema file to use. Could be a local file or a file hosted on a webserver.

    optional arguments:
    -h, --help            show this help message and exit
    --count COUNT         number of objects to create (default: 1)
    --mode {pure,mongo,full}
                            format of non-string data to emit. pure is normal JSON; dates emitted as ISO8601 strings and numbers are just numbers. mongo is mongoDB-compatible where dates are emitted as a special map {"$date",
                            millis}. mongoimport is sensitive to maps with $ keys and will process the content as the indicated type. full is a superset of mongoDB types. Integers are emitted as {"$int", value}, floats as
                            {"$float", value}. mongoimport does not permit this -- but pymonimport does.
    --defaultStringIpsum {word,sentence,paragraph,fname}
                            default style of string to emit when presented with type:string.
    -c COLLECTION, --collection COLLECTION
                            collection to import into (default: test)
    -d DB, --db DB        database to use (default: test)
    --host HOST           hostname to connect to (default: 127.0.0.1)
    --port PORT           port to connect to (default: 27017)
    --drop                drop the collection first before importing into it (default: False)
    --upload              upload to mongoDB server (default: False)

Generate json datas from default template
------------------------------------------

.. code-block:: console

    (.venv) $ mongo_ipsum --count 5 src/mongo_ipsum/models/hello.jsch
    {"productName": "course", "productDesc": "expertise The either across count found lake Climate various terrain known", "productDate":
    {"$date": 1160127987353}, "productID": "d2f54acf-a3c0-409e-a311-6cdff97a795d"}

Generate json datas from remote jsch file and upload with default value
------------------------------------------------------------------------

.. code-block:: console

    (.venv) $ mongo_ipsum --upload --drop https://raw.githubusercontent.com/hdeheer/mongo_ipsum/master/customer.jsch
    {"fname": "paul", "lname": "debbie", "email": "jane@linuxfoundation.org ", "phone": "332-805-4804", "gender": "X", "address":
    {"province": "Overijssel"}, "level": "bronze", "last_login": {"$date": 1586174645272}, "status": "INACTIVE"}
