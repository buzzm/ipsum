import random
import uuid
import datetime
from dateutil import parser

class Ipsum:
    """Given a python dictionary containing a structure that conforms to the
emerging v4 json-schema.org spec, generate one randomly or intelligently 
populated data structure.  In other words, use the metadata to create a piece
of data.  Some internal state is maintained across calls to createItem() to
speed things and provide additional functionality.

I have made two extensions:

type:poly
items: [ list of types ]
This supports polymorphic construction of JSON.  One of types in the array
will be chosen at random.

integer ipsum action
    "msgnum": {
      "type": "integer",
      "ipsum": { "inc": "A" }
      },

Instead of getting a random value, a counter named A will be used, where
the value starts at zero and increments with each call to Ipsum.createItem()
(i.e. it is stateful)
"""

    bleck = ["kilometre","languageThe","largest","linguistically","logging","mainland","making","metropolitan","mile)","million","more","most","municipality","named","nearby","not","of","on","one","or","original","people","per","populated","populous","railhead","railway","reach","recorded","renamed","residents","sawmill","seaport","settlement","site","speak","square","tavern","than","that","the","their","third","those","to","townsite","transcontinental","was","with","would"]

    fnames = [ "buzz", "richard", "bob", "edouard", "sam", "kay", "andre", "zach", "matt", "daniel", "allen", "jake", "carol", "francesca", "paul", "ron", "max", "steve", "david", "eliot", "todd", "bruce", "lenny", "victor", "alice", "jane", "mary", "jennifer", "chye", "ying", "robin", "lydia", "audrey", "amy", "kevin", "lauren", "stephanie", "kirsten", "julia" ]

    emailproviders = [ "gmail.com", "yahoo.com", "aol.com", "hotmail.com", "mongodb.com", "oracle.com" ]

    RAW = 0 
    PURE_JSON = 1
    MONGO_JSON = 2
    FULL_EXT_JSON = 3


    DEF_MIN_ARR_LEN = 1
    DEF_MAX_ARR_LEN = 4

    def __init__(self, params):
        """params is dict with the following structure:
mode: optional: one of "pure","mongo","full","raw".   pure generates a 
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
      """
        self.lowDateEpoch = 0
        self.highDateEpoch = int(datetime.datetime.now().strftime('%s'))
        self.counters = {}
        self.mode = self.MONGO_JSON

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



    def randomFrom(self, arr):
        return arr[self.randomInt(0, len(arr) - 1)]

    def randomInt(self, low, high):
	return int(random.random() * (high+1 - low) + low)

    def randomLong(self, low, high):
	return long(random.random() * (high+1 - low) + low)

    def randomDouble(self, low, high):
	return random.random() * (high - low) + low



    def makeIpsumString(self, ipsum):
        mode = "sentence"
        s = None

        if ipsum != None:
            mode = ipsum

	if mode == "sentence":
	    n = self.randomInt(0, len(self.bleck))
            s = ' '.join([self.randomFrom(self.bleck) for num in xrange(n)])

        elif mode == "word":
            s = self.randomFrom(self.bleck)

        elif mode == "fname":
            s = self.randomFrom(self.fnames)

        elif mode == "id":
	    s = str(uuid.uuid4())

	return s



    def makeFormattedString(self, fmt):
        oo = None

	if fmt == "phone":
	    oo = "%03d-%03d-%04d" % (self.randomInt(200,900),
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

        if type == "string":
            fmt = None
            v = None

            if "format" in info:
                fmt = info['format']

            if "enum" in info:
                v = self.randomFrom(info['enum']) # v is no longer None

            # date-time is special.  VERY special...
            if fmt == "date-time":
                if v is not None:   # must have been an enum; parse!
                    dt = parser.parse(v)
                    epoch = int(dt.strftime('%s'))
                else:
                    if 'ipsum' in info:  # if we have ipsum...
                        q = info['ipsum']
                        if 'inc' in q: # ...AND we have inc then OK!
                            q2 = q['inc']  #i.e. { "start": 0, "val": 1 }
                            if path not in self.counters:
                                dt = parser.parse(q2['start'])
                                epoch = int(dt.strftime('%s'))
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

                                self.counters[path] += v2

                            epoch = self.counters[path]

                    # was no ipsum or no ipsum.inc...
                    else:
                        epoch = self.randomLong(self.lowDateEpoch, self.highDateEpoch)


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
                    t = info['ipsum'] if 'ipsum' in info else "sentence"
                    o = self.makeIpsumString(t)

            else:
                o = v


        elif type == "object":
            ss = info["properties"]
            nn = {}
            self.processObject(nn, path, ss)
            o = nn;
            

        elif type == "array":
            ss = info["items"]
            mmin = ss['minItems'] if 'minItems' in ss else self.DEF_MIN_ARR_LEN
            mmax = ss['maxItems'] if 'maxItems' in ss else self.DEF_MAX_ARR_LEN
            
            # List comprehensions front and center....
            o = [ self.makeThing(path + "." + str(i), ss) for i in xrange( self.randomInt(mmin, mmax)) ]
            
        elif type == "poly":
            ll = info["items"]  # A list, not a dict!
            x = self.randomFrom(ll) # pick one and go!
            o = self.makeThing(path, x)
            

        elif type == "integer":
            v = None

            if "enum" in info:
                l = info['enum']
                v = l[self.randomInt(0, len(l) - 1)]

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
                v = self.randomInt(mmin,mmax)

            # At this point, we have SOME kind of v!
            if self.mode == self.FULL_EXT_JSON:
                o = { "$int": v }
            else:
                o = v


        elif type == "number":
            v = None

            if "enum" in info:
                l = info['enum']
                v = l[self.randomInt(0, len(l) - 1)]
                
            if v == None:
                mmin = info['minimum'] if 'minimum' in info else -100
                mmax = info['maximum'] if 'maximum' in info else 100
                v = self.randomDouble(mmin,mmax)

            # At this point, we have SOME kind of v!
            if self.mode == self.FULL_EXT_JSON:
                o = { "$float": v }
            else:
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


    def createItem(self, schema):
        # This is sort of "kick starts" things by diving into it
        # assuming the top level construct is an object....
	m = {}
	ss = schema["properties"]
	self.processObject(m, "", ss)
	return m
