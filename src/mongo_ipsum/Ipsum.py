# -*- coding: utf-8 -*-
import random
import os
import uuid
import datetime
import time
import struct
from dateutil import parser

class Ipsum:
    """Given a python dictionary containing a structure that conforms to the
emerging v4 json-schema.org spec, generate one randomly or intelligently
populated data structure.  In other words, use the metadata to create a piece
of data.  Some internal state is maintained across calls to createItem() to
speed things and provide additional functionality.
"""

    RAW = 0
    PURE_JSON = 1
    MONGO_JSON = 2
    FULL_EXT_JSON = 3


    DEF_MIN_ARR_LEN = 1
    DEF_MAX_ARR_LEN = 4

    def __init__(self, params):
        """params is dict with the following structure:
mode: optional: one of pure,mongo,full,raw
pure generates a
structure of types that is pure JSON compliant.  String, int, number, and
objects/array only, so dates and things are stringified.   mongo generates
mongoDB JSON type-marker convention entries e.g. {"$date": epoch}.  full
generate JSON type-marker entries for ALL non-string types e.g.
{"$long": 78374628734633} (mongoimport will NOT digest these extended types
but pymonimport will).   raw does not perform any JSON-readiness on the
types in the structure, e.g. dates remain in the returned structure as
datetime objects, not epoch ints or mongo-ish things.  This mode CAN be
used, however, to supply a returned structure directly to the insert()
method of the mongoDB python driver!

defaultStringIpsum: optional: one of sentence,paragraph,word,fname,id
The default ipsum for strings is word because most string fields are
single short-ish things.  If that's not your case, you can switch it.
Of course, you can always individually set a field ipsum or, with some
knowledge of the field, perhaps create an enum set.
      """

        self.counters = {}
        self.mode = self.MONGO_JSON
        self.dsi = "word"

        self.pid = os.getpid()
        self.oidinc = random.randint(0, 0xFFFFFF)

        if 'mode' in params:
            v = params['mode']
            if v == 'mongo':
                self.mode = self.MONGO_JSON
            elif v == 'pure':
                self.mode = self.PURE_JSON
            elif v == 'full':
                self.mode = self.FULL_EXT_JSON
            elif v == 'raw':
                self.mode = self.RAW

        #  Um, yeah, about this....
        #  So if we are creating numbers for JSON ASCII output like
        #  {$date: 24223334322} then those numbers have to be in millis
        #  for mongoimport (and mongomtimport!).   But if we are in raw
        #  mode, the python driver wants things granular only to seconds!
        self.millisAdj = 1000 if self.mode != self.RAW else 1

        self.lowDateEpoch = 60 * 60 * 24 * self.millisAdj   # force 1970-01-02 (in millis)
        self.highDateEpoch = int(datetime.datetime.now().strftime('%s')) * self.millisAdj

        if 'defaultStringIpsum' in params:
            self.dsi = params['defaultStringIpsum']



    def generateMongoOID(self):
        """Shamelessly lifted from bson python source to avoid dependency hell
        """
        oid = ""

        # 4 bytes current time
        oid += struct.pack(">i", int(time.time()))

        # 3 bytes machine
        #oid += ObjectId._machine_bytes
        oid += "ABC"

        # 2 bytes pid
        oid += struct.pack(">H", self.pid % 0xFFFF)

        # 3 bytes inc
        oid += struct.pack(">i", self.oidinc)[1:4]
        self.oidinc = (self.oidinc + 1) % 0xFFFFFF

        return oid.encode("hex")


    def str2Epoch(self, strdatetime):
        dt = parser.parse(strdatetime)
        return int(dt.strftime('%s')) * self.millisAdj

    def randomFrom(self, arr):
        return arr[self.randomInt(0, len(arr) - 1)]

    def randomInt(self, low, high):
        return int(random.random() * (high+1 - low) + low)

    # def randomLong(self, low, high):
    #     return long(random.random() * (high+1 - low) + low)

    # def randomDouble(self, low, high):
    #     return random.random() * (high - low) + low

    def makeIpsum(self, ipsum):
        style = self.dsi  # default
        s = None

        if ipsum != None:
            style = ipsum

        if style == "sentence":
            n = self.randomInt(10, 20)
            s = ' '.join([self.randomFrom(self.bleck) for num in range(n)])

        elif style == "paragraph":
            n = self.randomInt(10, len(self.bleck))
            s = ' '.join([self.randomFrom(self.bleck) for num in range(n)])

        elif style == "word":
            s = self.randomFrom(self.bleck)

        elif style == "fname":
            s = self.randomFrom(self.fnames)

        elif style == "id":
            s = str(uuid.uuid4())

        elif style == "bson:ObjectId" or style == "bson:7":
            v = self.generateMongoOID()

            if self.mode == self.PURE_JSON:
                s = v
            else:
                # oooo   not a string, but a dict!
                s = { "$oid": v }

        else:
            s = "unknown_ipsum \"" + style + "\""

        return s

    def makeFormattedString(self, fmt):
        oo = None

        if fmt == "phone":
            oo = "%03d-%03d-%04d" % (
                self.randomInt(200,900),
                self.randomInt(200,900),
                self.randomInt(100,9999))

        elif fmt == "uri":
            oo = "http://foo.bar.com/baz"   # NEED TO MAKE RANDOM

        elif fmt == "email":
            oo = "%s@%s" % (self.randomFrom(self.fnames),
                                self.randomFrom(self.emailproviders))

        return oo



    def makeThing(self, path, info):
        type = info["type"]

        if type == "null":
            o = "null"

        elif type == "string":
            fmt = None
            v = None

            if "format" in info:
                fmt = info['format']

            # date-time is special.  It is good to have optimizations
            # because running the parser over and over again on the
            # string rep of a date is very very slow...
            if "enum" in info:
                if fmt == "date-time":
                    if '_dateEnums' not in info:
                        info['_dateEnums'] = [ self.str2Epoch(ss) for ss in info['enum'] ]

                    v = self.randomFrom(info['_dateEnums']) # pick
                else:
                    v = self.randomFrom(info['enum']) # v is no longer None

            if fmt == "date-time":
                if v is not None:   # must have been an enum; parse!
                    epoch = v    #self.str2Epoch(v)
                else:
                    if 'ipsum' in info:  # if we have ipsum...
                        q = info['ipsum']
                        if 'inc' in q: # ...AND we have inc then OK!
                            q2 = q['inc']  #i.e. { "start": 0, "val": 1 }
                            if path not in self.counters:
                                epoch = self.str2Epoch(q2['start']) # expensive
                                self.counters[path] = epoch
                            else:
                                if 'secs' in q2:
                                    v2 = q2['secs']
                                if 'mins' in q2:
                                    v2 = q2['mins'] * 60
                                if 'hrs' in q2:
                                    v2 = q2['hrs'] * 60 * 60
                                if 'days' in q2:
                                    v2 = q2['days'] * 60 * 60 * 24

                                v2 *= self.millisAdj

                                self.counters[path] += v2

                            epoch = self.counters[path]

                    # was no ipsum or no ipsum.inc...
                    else:
                        # try for min and max.  To avoid running the expensive
                        # parse over and over, look for _min and _max (which only
                        # we can create).  Don't believe it?  Try commenting out
                        # the assignments below (lines ending with #tag1) and
                        # rerun.  It's almost 3x (300%) faster when you parse and
                        # save the value....
                        mmin = self.lowDateEpoch
                        mmax = self.highDateEpoch

                        if '_min' in info:
                            mmin = info['_min']
                        else:
                            if 'minimum' in info:
                                mmin = self.str2Epoch(info['minimum']) # expensive
                                info['_min'] = mmin  #tag1

                        if '_max' in info:
                            mmax = info['_max']
                        else:
                            if 'maximum' in info:
                                mmax = self.str2Epoch(info['maximum']) # expensive
                                info['_max'] = mmax  #tag1

                        epoch = self.randomLong(mmin, mmax)


                if self.mode == self.FULL_EXT_JSON or self.mode == self.MONGO_JSON:
                    o = { "$date": epoch }
                elif self.mode == self.RAW:
                    o = datetime.datetime.fromtimestamp(epoch)
                else:
                    o = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%dT%H:%M:%S')

            elif v is None:  # not date-time and not enum
                if fmt is not None:
                    # format takes precedence over ipsum field:
                    o = self.makeFormattedString(fmt)
                else:
                    t = info['ipsum'] if 'ipsum' in info else None
                    o = self.makeIpsum(t)

            else:
                o = v


        elif type == "object":
            ss = info["properties"]
            nn = {}
            self.processObject(nn, path, ss)
            o = nn


        elif type == "array":
            ss = info["items"]
            mmin = ss['minItems'] if 'minItems' in ss else self.DEF_MIN_ARR_LEN
            mmax = ss['maxItems'] if 'maxItems' in ss else self.DEF_MAX_ARR_LEN

            # List comprehensions front and center....
            o = [ self.makeThing(path + "." + str(i), ss) for i in range( self.randomInt(mmin, mmax)) ]

        elif type == "oneOf":
            ll = info["items"]  # A list, not a dict!
            x = self.randomFrom(ll) # pick one and go!
            o = self.makeThing(path, x)

        elif type == "number" or type == "integer":
            v = None

            if "enum" in info:
                v = self.randomFrom(info['enum']) # v is no longer None

            elif "ipsum" in info:
                q = info['ipsum']
                if 'inc' in q:
                    q2 = q['inc']  #i.e. { "start": 0, "val": 1 }
                    if path not in self.counters:
                        self.counters[path] = q2['start']
                    else:
                        self.counters[path] += q2['val']
                    v = self.counters[path]

            if v == None:
                mmin = info['minimum'] if 'minimum' in info else -100
                mmax = info['maximum'] if 'maximum' in info else 100
                if type == "number":
                    v = self.randomDouble(mmin,mmax)

                if type == "integer":
                    v = self.randomInt(mmin,mmax)


            # At this point, we have SOME kind of v!
            if self.mode == self.FULL_EXT_JSON:
                if type == "number":
                    o = { "$float": v }

                if type == "integer":
                    o = { "$int": v }

            else:
                o = v


        elif type == "boolean":
            v = None
            if "enum" in info:
                q = str(self.randomFrom(info['enum'])) # Force to str....
                v = q.lower() in ("yes", "true", "t", "1")
                # v is no longer None but a bool
            if v == None:
                v = True if self.randomDouble(0,1) > .5 else False
            o = v

        return o

    def processObject(self, target, currentPath, schema):
        for key, info in schema.iteritems():
            v = 100
            threshold = 100
            if "pctRandomNull" in info:
                v = random.random() * 100
                threshold = info['pctRandomNull']

            if v >= threshold:
                ncp = currentPath + '.' + key
                oo = self.makeThing(ncp, info)
                target[key] = oo


    def createItem(self, schema) -> dict:
        """ This is sort of "kick starts" things by diving into it
        assuming the top level construct is an object....
        """
        m = {}
        ss = schema["properties"]
        self.processObject(m, "", ss)
        return m
