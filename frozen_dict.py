if 3 / 2 == 1:
    __version__ = 2
    from itertools import imap

elif 3 / 2 == 1.5:
    __version__ = 3
    imap = map
    from functools import reduce
    xrange = range

# collections.Mapping seems like a pretty useless base class
# but the python community seems to love it, so I'll register
# FrozenDict as a subclass of Mapping.
from collections import Mapping

import itertools as it
from operator import itemgetter, methodcaller, attrgetter
from bisect import bisect_left

from_iterable = it.chain.from_iterable

flipped = itemgetter(1,0)
pop_first = methodcaller('pop', 0)
pop_last = methodcaller('pop', -1)
hash_caller = methodcaller('__hash__')

key_getter = attrgetter('key')
val_getter = attrgetter('value')
pair_getter = attrgetter('pair')

class Item(tuple):
    key   = property(itemgetter(0))
    value = property(itemgetter(1))
    pair  = property(itemgetter(0,1))
    __slots__ = ()
    def __hash__(self):
        return hash(self.key)
        
f_iter = frozenset.__iter__
class Group(frozenset):
    ''' Container to store multiple items during a hash collision.'''
    __slots__ = ()
    def __new__(cls, items):
        wrapped = map(Item, items)
        return frozenset.__new__(cls, wrapped)
    def __iter__(self):
        return self.items()
    def items(self):
        return imap(pair_getter, f_iter(self))
    def __hash__(self):
        frz = frozenset(self.items())
        return hash(frz)
    def __repr__(self):
        return frozenset.__repr__(self)

t_iter = tuple.__iter__
class Single(tuple):
    ''' The singleton counterpart to "Group".  This is a regular tuple,
        except the iteration is overloaded so that (key, value)
        actually iterates as though it were ((key, value),)
        
        This is done because the method FrozenDict.__getitem__
        loops through either a Single or Group looking for a
        matching key.
        
        I could store single items inside single-element frozensets
        but that would be a huge waste of space and resources.
       
        In testing 5 million hashes I only found collisions in 1/1400 items.
    '''
      
    key   = property(itemgetter(0))
    value = property(itemgetter(1))
    pair  = property(itemgetter(0,1))
    __slots__ = ()
    def __iter__(self):
        return t_iter((self.pair,))
    def __len__(self):
        return 1
    def __repr__(self):
        return 'Single(%r, %r)' % self.pair

def col(i):
    # We can't use itemgetter when we've overloaded
    # __getitem__ so we need to bind the method
    # directly from tuple.
    g = tuple.__getitem__
    def _col(self):
        return g(self,i)
    return _col

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

class FrozenDict(tuple):
    __doc__ = doc_str
    __slots__ = ()
    _hashes = property(col(0))
    _groups  = property(col(1))

    @staticmethod
    def item_adder(dct, item):
        ''' This is an agg function which groups items by the hash of the key.'''
        h = hash(item[0])
        if h not in dct:
            dct[h] = [item]
        else:
            dct[h].append(item)
        return dct

    @staticmethod
    def grouper(dct, h):
        ''' Unpacks the items for each hash value.  The groups that have 
            only one item are stored in a subclass of tuple.
            The ones with multiple items are put into a subclass of frozenset.'''
        grp = dct[h]
        if len(grp) == 1:
            ''' Most groups contain only a single item
                So we simply unpack it from its original
                container which speeds up lookup time.'''
            grp = Single(grp[0])
        else:
            ''' In the .01% of cases where a hash collision has occurred
                The items are stored inside a subclass of frozenset.'''
            grp = Group(grp)
        dct[h] = grp
        return dct

    def __new__(cls, orig = {}, **kw):
        if orig and kw:
            raise ValueError('You can only pass an iterable, or keyword arguments, not both.')
        elif orig and not kw:
            try:
                items = orig.items()
            except AttributeError:
                items = orig
        elif kw and not orig:
            items = kw.items()
        else:
            items = []

        dct = reduce(cls.item_adder, items, {})
        length = sum(map(len, dct.values()))
        dct = reduce(cls.grouper, tuple(dct), dct)
        dct = list(map(list, dct.items()))
        dct.sort(key=itemgetter(0))
        
        hashes = tuple(map(pop_first, dct))
        items = tuple(map(pop_first, dct))
        t = (hashes,items,length)
        return tuple.__new__(cls,t)

    def hashes(self):
        return tuple.__iter__(self._hashes)

    def groups(self):
        return tuple.__iter__(self._groups)

    def items(self):
        return from_iterable(self.groups())

    def keys(self):
        return map(itemgetter(0), self.items())
        
    def values(self):
        return map(itemgetter(1), self.items())

    def __iter__(self):
        return map(itemgetter(0), self.items())
        
    def __getitem__(self, key):
        try:
            x = hash(key)
            idx = bisect_left(self._hashes, x)
            for k0, v0 in self._groups[idx]:
                if k0 == key:
                    return v0
        except IndexError:
            pass
        raise KeyError(key)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def get(self, key, d = None):
        try:
            return self[key]
        except KeyError:
            return d
    
    def __repr__(self):
        cls = self.__class__.__name__
        f = lambda i: '%r : %r' % i
        _repr = ', '.join(map(f, self.items()))
        return '%s({%s})' % (cls, _repr)
        
    def __eq__(self, other):
        if not isinstance(other, FrozenDict):
            other = FrozenDict(other)
        return tuple.__eq__(self, other)
        
    def __hash__(self):
        return hash(self._groups)
        
    def __len__(self):
        return tuple.__getitem__(self, 2)

    @classmethod        
    def fromkeys(cls, keys, value):
        return cls(dict.fromkeys(keys, value))


if __version__ == 3:
    Mapping.register(FrozenDict)

if __version__ == 2:
    iterkey_getter = col(0)
    itervalue_getter = col(1)
    iteritem_getter = col(slice(None,2))

    class Python2(tuple):
        __doc__ = doc_str
        tuple_getter = tuple.__getitem__
        
        def __iter__(self):
            return imap(itemgetter(0), self.iteritems())

        def iterhashes(self):
            return iter(tuple.__iter__(self._hashes))
    
        def itergroups(self):
            return iter(tuple.__iter__(self._groups))
    
        def iteritems(self):
            return iter(from_iterable(self.itergroups()))
    
        def iterkeys(self):
            return imap(itemgetter(0), self.iteritems())
            
        def itervalues(self):
            return imap(itemgetter(1), self.iteritems())

        def hashes(self):
            return list(self.iterhashes())
            
        def groups(self):
            return list(self.itergroups())
            
        def keys(self):
            return list(self.iterkeys())
            
        def values(self):
            return list(self.itervalues())
            
        def items(self):
            return list(self.iteritems())

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
    Mapping.register(FrozenDict)

if __name__ == '__main__':
    frz = FrozenDict(imap(lambda i: (str(i),i), xrange(10**6)))
    dct = dict(imap(lambda i: (str(i),i), xrange(10**6)))
    
