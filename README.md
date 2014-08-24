ipsum
=====

Python utils to create random JSON data and import into mongoDB.
The overall structure and feature basis for ipsum is based on the JSON 
Schema spec at http://json-schema.org and basically runs it "in reverse":
instead of validating content against the spec, the spec is used to
generate randomized content.

Basic use:

```
$ python ./pygenipsum.py --count 6 shape4.jsch
$ python ./pygenipsum.py --mode full shape1.jsch
```

Dump and load a file:

```
$ python ./pygenipsum.py --count 6 shape3.jsch > /tmp/z
$ python ./pymonimport.py -d mydb -c foo2 --drop /tmp/z
```

If you don't want to preserve a random set (i.e. to load the same set
over and over again), go for direct util:

```
$ python ./pymonipsum.py -d mydb -c foo2 --drop --count 6 shape3.jsch
```

The shape files in this directory offer examples of how to use the various
ipsum features.  Formal documentation is forthcoming.  It is recommended to
try each a count of 4 to get a sense of what is going on.

Sometimes you have an existing JSON doc from which you want to "reverse" a schema.
There is an existing tool at the following URL which is very handy for that: http://www.jsonschema.net
