import cython
from abc import ABCMeta
from collections import Mapping
from sys import getsizeof

if 3 / 2 == 1:
    __version__ = 2
elif 3 / 2 == 1.5:
    __version__ = 3

cdef class _FrozenDict:
    __slots__ = ()
    cdef object d
    cdef long long h

    def __init__(self, *args, **kw):
        self.d = dict(*args, **kw)
        self.h = -1

    def __len__(self):
        return len(self.d)

    def __iter__(self):
        return iter(self.d)

    def __getitem__(self, key):
        return self.d[key]

    def __contains__(self, key):
        return (key in self.d)

    def __hash__(self):
        if self.h == -1:
            items = ((k,self[k]) for k in self)
            self.h = hash(frozenset(items))
        return self.h

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.d)

    def __sizeof__(self):
        return getsizeof(self.d) + getsizeof(self.h)

class FrozenDict(_FrozenDict):
    __slots__ = ()
    __hash__ = _FrozenDict.__hash__
    def __eq__(self, other):
        # The __eq__ is explicitly defined because the 
        # method in Mapping uses dict(self) == dict(other)
        # which relies too much on copying, and is slow.
        if not isinstance(other, Mapping):
            return NotImplemented

        if len(self) != len(other):
            return False
        try:
            return all((self[k] == other[k] for k in self))
        except KeyError:
            return False
            
    def copy(self):
        return type(self)(self)
        
    @classmethod
    def fromkeys(cls, keys, value):
        return cls(dict.fromkeys(keys, value))

#  We want to mix the rest of the methods from the abstract
# base class "Mapping" without directly inheriting from it.
# instances of "Mapping", and probably other ABCMeta classes
# don't have __slots__ = ().  This means that ever instance
# of a FrozenDict will have an extra __dict__ attribute.
#
# Here we use set comprehension to mix in all the missing
# methods, and then we rebuild the class "FrozenDict" by
# calling the "type" function.

ABC = ABCMeta('ABC',(),{})
keys = set(dir(Mapping)) - set(dir(ABC))
keys = keys - {'__metaclass__'}
keys = keys - set(_FrozenDict.__dict__)
dct = {k: getattr(Mapping, k) for k in keys}
dct.update(FrozenDict.__dict__)
FrozenDict = type('FrozenDict', (_FrozenDict,), dct)
Mapping.register(FrozenDict)

__all__ = ['FrozenDict']