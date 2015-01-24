if 3 / 2 == 1:
    __version__ = 2
    from itertools import imap

elif 3 / 2 == 1.5:
    __version__ = 3
    imap = map
    
def on_error_plain(func):
    ''' Prevents a problem with the object's "repr" function from 
        bringing everything to a screeching halt.'''
    def __repr__(self):
        try:
            return func(self)
        except Exception:
            return object.__repr__(self)
    return __repr__
    
from operator import itemgetter, methodcaller, attrgetter
from bisect import bisect_left, bisect_right
hash_caller = methodcaller('__hash__')

def tuple_getter(i):
    # We can't use itemgetter when we've overloaded
    # __getitem__ so we need to bind the method
    # directly from tuple.
    g = tuple.__getitem__
    def _col(self):
        return g(self,i)
    return _col

hash_getter = tuple_getter(0)
pair_getter = tuple_getter(1)

pop_first = methodcaller('pop', 0)
pop_last = methodcaller('pop', -1)
col_0 = itemgetter(0)
col_1 = itemgetter(1)
col_2 = itemgetter(2)
col_3 = itemgetter(3)
cols_1_2 = itemgetter(1,2)
flipped = itemgetter(1,0)

doc_str = '''\
Behaves in most ways like a regular dictionary, except that it's immutable.
It differs from other implementations because it doesn't subclass "dict".
Instead it subclasses "tuple" which guarantees immutability, and the items
are sorted based off the hash of the key, which maintains fast lookup times.

FrozenDict instances are created with the same arguments used to initialize
regular dictionaries, and has all the same methods.
    [in]  >>> f = FrozenDict(x=3,y=4,z=5)
    [in]  >>> f['x']
    [out] >>> 3
    [in]  >>> f['a'] = 0
    [out] >>> TypeError: 'FrozenDict' object does not support item assignment

FrozenDict can accept un-hashable values, but FrozenDict is only hashable if its values are hashable.
    [in]  >>> f = FrozenDict(x=3,y=4,z=5)
    [in]  >>> hash(f)
    [out] >>> 646626455
    [in]  >>> g = FrozenDict(x=3,y=4,z=[])
    [in]  >>> hash(g)
    [out] >>> TypeError: unhashable type: 'list'

FrozenDict interacts with dictionary objects as though it were a dict itself.
    [in]  >>> original = dict(x=3,y=4,z=5)
    [in]  >>> frozen = FrozenDict(x=3,y=4,z=5)
    [in]  >>> original == frozen
    [out] >>> True

FrozenDict supports bi-directional conversions with regular dictionaries.
    [in]  >>> original = {'x': 3, 'y': 4, 'z': 5}
    [in]  >>> FrozenDict(original)
    [out] >>> FrozenDict({'x': 3, 'y': 4, 'z': 5})
    [in]  >>> dict(FrozenDict(original))
    [out] >>> {'x': 3, 'y': 4, 'z': 5}   '''
    
class Item(tuple):
    ''' A special container to make all items hashable.
        We put all the dict entries into a set and 
        record the order in which they are iteratively
        returned. The items are eventually stored inside
        a tuple, but this ensures that everything is sorted
        consistently before calculating the hash of 
        the entire dictionary.'''
        
    h = property(col_0)
    key = property(col_1)
    value = property(col_2)
    pair = property(cols_1_2)

    def __new__(cls, pair):
        key, value = pair
        h = hash(key)
        t = (h, key, value)
        return tuple.__new__(cls, t)

    def __hash__(self):
        return self[0]
        
    def __cmp__(self, other):
        try:
            d_hash = self[0] - hash(other)
            if d_hash < 0:
                return -1
            if d_hash > 0:
                return 1
            
            #Now we're into hash collisions
            self_key = self[1]
            other_key = other.key
            if self_key < other_key:
                return -1
            if self_key > other_key:
                return 1
                
            # Before checking whether the 
            # the two keys, stick it into a set
            #and see which one is returned first
            item = {self_key, other_key}.pop()
            if item is self_key:
                return -1
            else:
                return 1

        except Exception:
            return None

    def __eq__(self, other):
         comp = self.__cmp__(other)
         return comp == 0
    
    def __lt__(self, other):
         comp = self.__cmp__(other)
         return comp == -1

    def __gt__(self, other):
        comp = self.__cmp__(other)
        return comp == 1

    @on_error_plain
    def __repr__(self):
        return 'Item((%r, %r))' % (self[1], self[2])
        
class FrozenDict(tuple):
    __doc__ = doc_str

    tuple_getter = tuple.__getitem__
    _hashes = property(hash_getter)
    _pairs = property(pair_getter)
    __slots__ = ()
    
    def __new__(cls, orig={}, **kw):
        #Sort the items by the hashes of their keys
        #The parent tuple has two items.
        #The first is a 
        if kw:
            if orig:
                d = dict(orig, **kw)
            else:
                d = kw
            orig, kw = None, None
            pairs = map(Item, d.items())
            del d

        else:
            try:
                pairs = map(Item, orig.items())
            except AttributeError:
                pairs = map(Item, orig)

        pairs = sorted(pairs)
        hashes = tuple(map(col_0, pairs))
        pairs = tuple(map(attrgetter('pair'), pairs))

        t = (hashes, pairs)
        return tuple.__new__(cls, t)
        
    def __hash__(self):
        return hash(self._pairs)

    def __eq__(self, other):
        if not isinstance(other, FrozenDict):
            other = FrozenDict(other)
        return tuple.__eq__(self, other)

    def __bisecter__(self, key, in_only=False, on_error_None=False):
        x = hash(key)
        lkp = tuple.__getitem__(self, 0) # self._hashes
        if (not self) or x < lkp[0] or x > lkp[-1]:
            if in_only:
                return False
            if on_error_None:
                return None
            else:
                raise KeyError(key)

        lo = bisect_left(lkp, x)
        hi = bisect_right(lkp, x, lo)
        if hi > lo:
            slc = lkp[lo:hi]
            assert set(slc) == {x}
            
            items = tuple.__getitem__(self, 1)[lo:hi]
            for k0,v0 in items:
                if k0 != key:
                    continue
                if in_only:
                    return True
                else:
                    return v0

        if in_only:
            return False
        if on_error_None:
            return None
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        return self.__bisecter__(key)
        
    def __contains__(self, key):
        return self.__bisecter__(key, in_only=True)

    def get(self, key):
        return self.__bisecter__(key,on_error_None=True)

    @on_error_plain
    def __repr__(self):
        fcn = lambda pair: '%r: %r' % pair
        cls_name = self.__class__.__name__
        _repr = ', '.join(map(fcn, self.items()))
        final = '%s({%s})' % (cls_name, _repr)
        return final
        
    def __len__(self):
        return len(hash_getter(self))

    def __iter__(self):
        return imap(col_0, self.items())
        
    def keys(self):
        return map(col_0, self.items())

    def values(self):
        return map(col_1, self.items())
        
    def items(self):
        itr = tuple.__iter__
        return itr(pair_getter(self))
        
    @classmethod        
    def fromkeys(cls, keys, value):
        return cls(dict.fromkeys(keys, value))

if __version__ == 2:
    class Python2(FrozenDict):
        __doc__ = doc_str
        tuple_getter = tuple.__getitem__
        
        def items(self):
            return list(pair_getter(self))

        def iterkeys(self):
            items = imap(pair_getter, self)
            return imap(col_0, items)

        def itervalues(self):
            items = imap(pair_getter, self)
            return imap(col_1, items)

        def iteritems(self):
            return imap(pair_getter, self)

        def has_key(self, key):
            return key in self

    #If this is Python2, rebuild the class
    #from scratch rather than use a subclass
    dct = FrozenDict.__dict__
    py3 = {k: dct[k] for k in dct}

    py2 = {'__doc__': doc_str}
    py2.update(py3)
    dct = Python2.__dict__
    py2.update({k: dct[k] for k in dct})
    
    FrozenDict = type('FrozenDict', (tuple,), py2)

if __name__ == '__main__':
    orig = dict({Item(('x',3)): 4, Item(('x',4)): 4}, a = 1, b= 2 ,c = 3)
 
