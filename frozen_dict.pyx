import cython
from abc import ABCMeta
from collections import Mapping, Set, KeysView, MappingView, ValuesView, ItemsView
from itertools import chain
from sys import getsizeof

cdef class BaseSet:
    def _from_iterable(self, it):
        return set(it)

    def __and__(self, other):
        inner = (k for k in self if k in other)
        return self._from_iterable(inner)

    def __sub__(self, other):
        left  = (k for k in self if k not in other)
        return self._from_iterable(left)

    def __xor__(self, other):
        left  = (k for k in self if k not in other)
        right = (k for k in other if k not in self)
        it = chain(left, right)
        return self._from_iterable(it)

    def __or__(self, other):
        inner = (k for k in self if k in other)
        left  = (k for k in self if k not in other)
        right = (k for k in other if k not in self)
        it = chain(left, inner, right)
        return self._from_iterable(it)

    def __rand__(self, other):
        return (self & other)

    def __ror__(self, other):
        return (self | other)
        
    def __rsub__(self, other):
        return (self - other)
        
    def __rxor__(self, other):
        return (self ^ other)

    def __richcmp__(self, other, int flag):
        switch = (flag != 3)

        try:
            if flag == 0:    # LESS THAN
                if len(self) >= len(other):
                    return False
                little, big = self, other

            elif flag == 1:  # LESS THAN OR EQUAL
                if len(self) > len(other):
                    return False
                little, big = self, other

            if flag == 2:    # EQUAL
                if len(self) != len(other):
                    return False
                little, big = self, other

            elif flag == 3:  # NOT EQUAL
                if len(self) != len(other):
                    return True
                little, big = self, other
                switch = False

            elif flag == 4:  # GREATER THAN
                if len(self) <= len(other):
                    return False
                little, big = other, self

            elif flag == 5:  # GREATER THAN OR EQUAL
                if len(self) < len(other):
                    return False
                little, big = other, self

        except TypeError:
            return NotImplemented

        # We don't check types, so we need
        # to make sure we haven't been checking
        # against either a sequence or a mapping
        # Looking up item "0" should raise a TypeError
        # if we're looking at an unordered collection
        try:
            other[0]
        except TypeError:
            pass
        except LookupError:
            # A LookupError includes both KeyError
            # and IndexError
            return NotImplemented
        else:
            return NotImplemented

        try:
            for k in little:
                if k not in big:
                    return (not switch)
            return switch
        except TypeError:
            return NotImplemented            

@cython.final
cdef class Keys(BaseSet):
    cdef FrozenDict frz
    def __cinit__(self, frz):
        self.frz = frz

    def __len__(self):
        return len(self.frz)

    def __repr__(self):
        c = self.__class__.__name__
        return '%s(%s)' % (c, list(self))

    property _mapping:
        def __get__(self):
            return self.frz

    def __iter__(self):
        for k in self.frz:
            yield k

    def __contains__(self, key):
        try:
            return (key in self.frz)
        except TypeError:
            return False

@cython.final
cdef class Items(BaseSet):
    cdef FrozenDict frz

    def __cinit__(self, frz):
        self.frz = frz

    def __len__(self):
        return len(self.frz)

    def __repr__(self):
        c = self.__class__.__name__
        return '%s(%s)' % (c, list(self))

    property _mapping:
        def __get__(self):
            return self.frz

    def __iter__(self):
        for k in self.frz:
            yield (k, self.frz[k])

    def __contains__(self, item):
        try:
            k, v = item
            return self.frz[k] == v
        except Exception:
            return False

@cython.final
cdef class Values:
    cdef FrozenDict frz
    def __cinit__(self, frz):
        self.frz = frz

    def __len__(self):
        return len(self.frz)

    def __repr__(self):
        c = self.__class__.__name__
        return '%s(%s)' % (c, list(self))

    property _mapping:
        def __get__(self):
            return self.frz

    def __iter__(self):
        for k in self.frz:
            yield self.frz[k]

    def __contains__(self, value):
        for k in self.frz:
            if self.frz[k] == value:
                return True
        return False

cdef class FrozenDict:
    ''' An immutable dictionary.  A builtin dictionary is wrapped
        at the C level, which makes it impossible to manipulate from
        Python.  This means that if the values are hashable, the 
        FrozenDict is hashable as well.  Item retrieval is within
        10 ns of a builtin dict.
    '''
    cdef object d
    cdef long long h

    def __cinit__(self, *args, **kw):
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
        c = self.__class__.__name__
        i = ('%r: %r' % (k, self[k]) for k in self)
        return '%s({%s})' % (c, ', '.join(i))

    def __sizeof__(self):
        return getsizeof(self.d) + getsizeof(self.h)

    cpdef _eq(self, FrozenDict other):
        return self.d == other.d

    def __richcmp__(self, other, int flag):
        # For fastest comparison of one FrozenDict to another.
        # We just compare the hidden underlying dictionaries
        # This makes comparisons slightly slower for regular
        # dictionaries because we raise and catch an error.
        try:
            if flag == 2:
                return self._eq(other)
            elif flag == 3:
                return not self._eq(other)
        except TypeError:
            pass

        # Check that "other" is either an instance of dict or FrozenDict
        # This logic is quicker than using the builtin "isinstance"
        mro = other.__class__.__mro__
        if (dict not in mro) and (FrozenDict not in mro):
            return NotImplemented

        switch = True
        if flag == 0:    # LESS THAN
            if len(self) >= len(other):
                return False
            little, big = self, other

        elif flag == 1:  # LESS THAN OR EQUAL
            if len(self) > len(other):
                return False
            little, big = self, other

        elif flag == 2:    # EQUAL
            if len(self) != len(other):
                return False
            little, big = self, other

        elif flag == 3:  # NOT EQUAL
            if len(self) != len(other):
                return True
            little, big = self, other
            switch = False

        elif flag == 4:  # GREATER THAN
            if len(self) <= len(other):
                return False
            little, big = other, self

        elif flag == 5:  # GREATER THAN OR EQUAL
            if len(self) < len(other):
                return False
            little, big = other, self

        try:
            for k in little:
                if little[k] != big[k]:
                    return not switch
            return switch
        except KeyError:
            return not switch

    def get(self, key, default=None):
        if key in self.d:
            return self.d[key]
        else:
            return default

    def copy(self):
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, value):
        return cls(dict.fromkeys(keys, value))

    ########################################
    #         Python 3 Methods             #
    ########################################
    """
    def keys(self):
        return Keys(self)

    def values(self):
        return Values(self)

    def items(self):
        return Items(self)
    #"""

    ########################################
    #         Python 2 Methods             #
    ########################################
    
    def has_key(self, key):
        return (key in self)

    def viewkeys(self):
        return Keys(self)

    def viewvalues(self):
        return Values(self)

    def viewitems(self):
        return Items(self)

    def iterkeys(self):
        return (k for k in self)

    def itervalues(self):
        return (self[k] for k in self)

    def iteritems(self):
        return ((k,self[k]) for k in self)

    def keys(self):
        return [k for k in self]

    def values(self):
        return [self[k] for k in self]

    def items(self):
        return [(k,self[k]) for k in self]
    #"""

Mapping.register(FrozenDict)
ValuesView.register(Values)
ItemsView.register(Items)
KeysView.register(Keys)




