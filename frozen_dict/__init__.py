'''Summary:
- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- Most implementations of FrozenDict simply subclass dict, or wrap a thin object around one.
- This implemtation is 100% thread safe.  It subclasses tuple.
- All bindings, other than the items themselves, are subclasses of tuple or frozenset.

Features:
- Hashability is possible, not required.  Like a tuple, FrozenDict accepts unhashable values.
- Works with both Python 2 and Python3.
- Supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is created with the same arguments that instantiate a regular dict. 
- Can replace an existing dictionary, assuming your code doesn't check types.
- Great for debugging.

Speed:
- Uses similar hash-table lookup methodology as a dict, O(1), and in pure Python.
- With strings as keys, 1.8 micro-sec to return a value from 1 million items.

Requirements:
- Python 2.6 or later, any version of Python3.
- Unit tested on 2.7 and 3.4.  Please report any bugs.

Python2 vs Python3:
- The same differences that are found in regular dictionaries.
- keys(), values(), and items() in Python3 return generators.
- keys(), values(), and items() in Python2 return lists.
- iterkeys(), itervalues(), and iteritems() do not exist in Python3.

Not Implemented Features:
- Python3: None
- Python2: viewkeys(), viewvalues(), and viewitems()
- These are legacy methods from Python2, discontinued in Python3.
- Those methods would require creating a new dict every time.
- If you want those methods, either modify my code or create your own subclass.

Methodology:
- A FrozenDict is a subclass of tuple, and it contains two main entries:
- One is a tuple where items are grouped and sorted by hash
- The other is a lookup table of those hashes.
- Most dict keys have a unique hash.  Approx 1/1400 collide on PC, far fewer on Mac.
- To return a value, the key is hashed, python's "bisect" finds the hash's index.
- Using that index, FrozenDict searched for the key among all the items in the group.
- If the key foud, it returns the value, otherwise a KeyError is raised.

Resolving Hash Collisions
- During a collision, items are placed in a subclass of frozenset, called "Group".
- "Group" can accept unhashable items, but will then no longer return a hash itself.
- Each key-value pair is put in a class "Item" which only hashes the key.
- This allows items with un-hashable values to be stored inside an unordered frozenset.
- When hashing "Group", the items are first unpacked into regular tuples.
- Then we put those items into a new frozenset and take that hash.
- If any item is unhashable, this is where we'll get an error.
'''

__all__ = ['FrozenDict','Item','Single','Group']

if 3 / 2 == 1:
    __version__ = 2
    from itertools import imap

elif 3 / 2 == 1.5:
    __version__ = 3
    imap = map
    from functools import reduce
    xrange = range

import gc
import itertools as it
from collections import Mapping, defaultdict
from operator import itemgetter, methodcaller, attrgetter
from bisect import bisect_left

from_iterable = it.chain.from_iterable

itemgetter_0 = itemgetter(0)
itemgetter_1 = itemgetter(1)
itemgetter_0_1 = itemgetter(0,1)

class Item(tuple):
    key   = property(itemgetter_0)
    value = property(itemgetter_1)
    pair  = property(itemgetter_0_1)
    __slots__ = ()
    def __hash__(self):
        return hash(self[0])
    def __repr__(self):
        return 'Item([%r, %r])' % self

f_iter = frozenset.__iter__
class Group(frozenset):
    ''' Container to store multiple items during a hash collision.'''
    __slots__ = ()
    _length = property(len)
    def __new__(cls, items):
        wrapped = map(Item, items)
        self = frozenset.__new__(cls, wrapped)
        keys = set(map(itemgetter_0, self))
        if len(keys) < len(self):
            key_list = list(map(itemgetter_0, self))
            args = [k for k in keys if key_list.count(k) > 1]
            line_1 = 'You have tried to create a frozen dictionary'
            line_2 = 'by mapping the same key to multiple values.'
            line_3 = 'Key(s) with inconsistent values: %s' % (args,)
            msg = '\n   '.join(['',line_1,line_2,line_3])
            raise ValueError(msg)
        if len(self) == 1:
            ''' Sometimes the same key-value pair is passed twice.
                In that event, "Group" needs to be converted to single
                so that equality still holds with other dictionaries
                where the key-value pair was only entered once.'''
            for item in self:
                return Single(item)
        return self

    def __iter__(self):
        return imap(itemgetter_0_1, f_iter(self))

    def __hash__(self):
        frz = frozenset(list(self))
        return hash(frz)

    def __repr__(self):
        cls = type(self).__name__
        return '%s(%r)' % (cls, list(self))

    def get(self, key):
        ''' Both "Group" and "Single" use the "get" feature
            to look for a key-value pair.  Only "Group" iterates
            through each item.  This is slow, but hash collisions
            are rare, so this is not a big deal.'''
        for k0, value in self:
            if k0 == key:
                return value
        raise KeyError(key)

    def has(self, key):
        ''' Like the "get" method but only checks for the existence of a key. '''
        for k0, value in self:
            if k0 == key:
                return True
        return False
        
        
t_iter = tuple.__iter__
t_get = tuple.__getitem__
class Single(tuple):
    ''' The singleton counterpart to "Group".  This is a regular tuple,
        except the iteration is overloaded so that (key, value)
        actually iterates as though it were ((key, value),)
        
        This is done so that FrozenDict can iterate over all the items
        regardless of whether a particular hash value has one item in it
        or ten.  Overloading the iterator saves space and speed,
        especially when compared with wrapping the single item in a second tuple.
    '''
    key   = property(itemgetter_0)
    value = property(itemgetter_1)
    pair  = property(itemgetter_0_1)
    _length = 1
    __slots__ = ()
    def __iter__(self):
        return t_iter((self.pair,))
    def __len__(self):
        return 1
    def get(self, key):
        if self[0] == key:
            return self[1]
        raise KeyError(key)
    def has(self, key):
        ''' Like the "get" method but only checks for the existence of a key. '''
        return self[0] == key
    def __repr__(self):
        return 'Single([%r, %r])' % self

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

t_eq = tuple.__eq__
t_new = tuple.__new__
t_iter = tuple.__iter__
_length = attrgetter('_length')

'''
__tget__ is actually tuple.__getitem__ which is manually bounded to FrozenDict
this is done because __getitem__ is overrideen in FrozenDict, so we can't 
use itemgetter. This is stll faster than calling tuple.__getitem__(self, i)'''
hash_getter = methodcaller('__tget__', 0)
group_getter = methodcaller('__tget__', 1)
length_getter = methodcaller('__tget__', 2)

if __version__ == 2:
    iteritems = methodcaller('iteritems')
elif __version__ == 3:
    iteritems = methodcaller('items')

class FrozenDict(tuple):
    __doc__ = doc_str
    __slots__ = ()
    _hashes = property(hash_getter)
    _groups  = property(group_getter)
    __tget__ = tuple.__getitem__

    @staticmethod
    def item_adder(dct, item):
        ''' This is an agg function which groups items by the hash of the key.'''
        dct[hash(item[0])].append(item)
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

    def __new__(cls, *args, **kw):
        if len(args) > 1:
            raise ValueError('The variable "args" can only contain one item.')
        if args:
            try:
                args = iteritems(args[0])
            except AttributeError:
                args = args[0]
        
        dct = reduce(cls.item_adder, args, defaultdict(list))
        del args
        dct = reduce(cls.item_adder, iteritems(kw), dct)
        del kw

        dct = reduce(cls.grouper, tuple(dct), dct)
        dct = sorted(iteritems(dct), key=itemgetter_0)
        items = tuple(imap(itemgetter_1, dct))
        hashes = tuple(imap(itemgetter_0, dct))
        del dct
        length = sum(imap(_length, items))
        return t_new(cls,(hashes,items,length))

    def hashes(self):
        return t_iter(self._hashes)

    def groups(self):
        return t_iter(self._groups)

    def items(self):
        return from_iterable(self.groups())

    def keys(self):
        return map(itemgetter_0, self.items())
        
    def values(self):
        return map(itemgetter_1, self.items())

    def __iter__(self):
        return map(itemgetter_0, self.items())

    def __getitem__(self, key):
        idx = bisect_left(hash_getter(self), hash(key))
        try:
            return group_getter(self)[idx].get(key)
        except IndexError:
            pass
        raise KeyError(key)

    def __contains__(self, key):
        idx = bisect_left(hash_getter(self), hash(key))
        try:
            return group_getter(self)[idx].has(key)
        except IndexError:
            return False

    def get(self, key, d = None):
        try:
            return self[key]
        except KeyError:
            return d
    
    def __repr__(self):
        cls = self.__class__.__name__
        f = lambda i: '%r: %r' % i
        _repr = ', '.join(imap(f, self.items()))
        return '%s({%s})' % (cls, _repr)
        
    def __eq__(self, other):
        if not isinstance(other, FrozenDict):
            try:
                other = FrozenDict(iteritems(other))
            except Exception:
                return False
        return group_getter(self) == group_getter(other)

    def __hash__(self):
        return hash(group_getter(self))

    def __len__(self):
        return length_getter(self)

    def copy(self):
        cls = type(self)
        t = tuple(t_iter(self))
        return t_new(cls, t)
        
    def as_tuple(self):
        ''' Allows somebody to see the inner workings.'''
        return tuple(t_iter(self))

    @classmethod
    def fromkeys(cls, keys, value):
        return cls(dict.fromkeys(keys, value))

if __version__ == 3:
    Mapping.register(FrozenDict)

if __version__ == 2:
    class Python2(tuple):
        __doc__ = doc_str
        
        def __iter__(self):
            return imap(itemgetter_0, self.iteritems())

        def iterhashes(self):
            return t_iter(self._hashes)
    
        def itergroups(self):
            return t_iter(self._groups)
    
        def iteritems(self):
            return iter(from_iterable(self.itergroups()))
    
        def iterkeys(self):
            return imap(itemgetter_0, self.iteritems())
            
        def itervalues(self):
            return imap(itemgetter_1, self.iteritems())

        def hashes(self):
            return list(self._hashes)
            
        def groups(self):
            return list(self._groups)
            
        def keys(self):
            return list(self.iterkeys())
            
        def values(self):
            return list(self.itervalues())
            
        def items(self):
            return list(self.iteritems())

        def has_key(self, key):
            return self.__contains__(key)

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