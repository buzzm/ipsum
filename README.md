ipsum
=====

Python utils to create random JSON data and import into mongoDB.
Get the python libs into a dir and try this:

# Basic use:
$ python ./pygenipsum.py --count 6 shape4.jsch
$ python ./pygenipsum.py --mode full shape1.jsch

# Dump and load a file:
$ python ./pygenipsum.py --count 6 shape3.jsch > /tmp/z
$ python ./pymonimport.py -d mydb -c foo2 --drop /tmp/z

# If you don't want to preserve a random set (i.e. to load the same set
# over and over again), go for direct util:
$ python ./pymonipsum.py -d mydb -c foo2 --drop --count 6 shape3.jsch
