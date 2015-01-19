'''
-  Compatible with both Python2 and Python3.
-  Creates a class that behaves like a dictionary, except all the mutable methods are removed.
-  The "read-only" bound methods are saved.  Then the original dictionary is deleted.
-  Like a tuple, FrozenDict is hashable if and only if all its items are hashable.
-  All the equality and comparison operators behave just like a normal dictionary.
-  FrozenDict is bidirectional, dict(FrozenDict(*args, **kw)) == dict(*args, **kw)
-  Methods such as copy and fromkeys return an instance of FrozenDict
'''

def enclose(func):
    return func()
    
@enclose
def FrozenDict():
    #We have to enclose this method in the class definition
    #because we are overriding both __iter__ and __getitem__
    g = tuple.__getitem__

    #We construct the class FrozenDict to work with Python3.x
    #If the runtime environment is Python2.x, we make some modifications
    #to the FrozenDict class before returning it.
    if 3 / 2 == 1:
        version = 2
    elif 3 / 2 == 1.5:
        version = 3

    class FrozenDict(tuple):
        __slots__ = ()
        def __new__(cls, *args, **kw):
            #Define a regular dictionary first
            #Make copies of all the important "read-only" bound methods
            #Delete the original dictionary, making it inaccessible
            #If there's a way to modify the underlying dictionary, 
            #then it's damn near impossible.
            d = dict(*args, **kw)
            k = d.keys
            v = d.values
            i = d.items
            g = d.__getitem__
            c = d.__contains__
            l = len(d)
            del d
            return tuple.__new__(cls,(k,v,i,g,c,l))

        def __iter__(self):
            return iter(g(self,0)())

        def keys(self):
            return iter(g(self,0)())

        def values(self):
            return iter(g(self,1)())

        def items(self):
            return iter(g(self,2)())

        def get(self, key):
            try:
                return g(self,3)(key)
            except KeyError:
                return None

        def __getitem__(self, key):
            return g(self,3)(key)

        def __contains__(self, key):
            return g(self,4)(key)

        def __len__(self):
            return g(self,5)

        def __hash__(self):
            return hash(frozenset(g(self,2)()))

        def __eq__(self, other):
            try:
                return dict(self) == dict(other)
            except TypeError:
                return dict(self) == other
            
        def __ne__(self, other):
            try:
                return dict(self) != dict(other)
            except TypeError:
                return dict(self) != other
                
        def __ge__(self, other):
            try:
                return dict(self) >= dict(other)
            except TypeError:
                return dict(self) >= other
                
        def __gt__(self, other):
            try:
                return dict(self) > dict(other)
            except TypeError:
                return dict(self) > other

        def __le__(self, other):
            try:
                return dict(self) <= dict(other)
            except TypeError:
                return dict(self) <= other
                
        def __lt__(self, other):
            try:
                return dict(self) < dict(other)
            except TypeError:
                return dict(self) < other

        def __repr__(self):
            cls = type(self).__name__
            _repr = repr(dict(self))
            return '%s(%s)' % (cls,_repr)
            
        def fromkeys(self, keys, value):
            d = dict.fromkeys(keys, value)
            return type(self)(d)

        def copy(self):
            return type(self)(self)        

        # "count" and "index" are built in to 'tuple', so we
        # we may as well override them into something useful.
        def count(self, value):
            return list(self.values()).count(value)
            
        def index(self, key):
            return list(self.values()).index(key)

    if version == 3:
        return FrozenDict
        
    @staticmethod
    def __new__(cls, *args, **kw):
        #Just like __new__ in Python3, except it returns iterkeys, itervalues, and iteritems
        d = dict(*args, **kw)
        k = d.iterkeys
        v = d.itervalues
        i = d.iteritems
        g = d.__getitem__
        c = d.__contains__
        l = len(d)
        del d
        return tuple.__new__(cls,(k,v,i,g,c,l))
    FrozenDict.__new__ = __new__

    def iterkeys(self):
        return iter(g(self,0)())
    def itervalues(self):
        return iter(g(self,1)())
    def iteritems(self):
        return iter(g(self,2)())
    FrozenDict.iterkeys = iterkeys
    FrozenDict.itervalues = itervalues
    FrozenDict.iteritems = iteritems

    def has_key(self, key):
        return g(self,4)(key)
    FrozenDict.has_key = has_key

    def keys(self):
        return list(self.iterkeys())
    def values(self):
        return list(self.itervalues())
    def items(self):
        return list(self.iteritems())
    FrozenDict.keys = keys
    FrozenDict.values = values
    FrozenDict.items = items

    def viewkeys(self):
        return dict(self).viewkeys()
    def viewvalues(self):
        return dict(self).viewvalues()
    def viewitems(self):
        return dict(self).viewitems()
    FrozenDict.viewkeys = viewkeys
    FrozenDict.viewvalues = viewvalues
    FrozenDict.viewitems = viewitems
    
    def __cmp__(self, other):
        return cmp(dict(self),dict(other))
    FrozenDict.__cmp__ = __cmp__
    
    return FrozenDict
