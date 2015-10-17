# FrozenDict

Summary:
- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- Most implementations of FrozenDict simply subclass dict, or wrap a thin object around one.
- This implemtation does the wrapping at the C level, making it impossible to change from Python.
- Use it like a regular dictionary, such as in this example:

``` python
from frozen_dict import FrozenDict
f = FrozenDict({'x':3, 'y':4, 'z': 5})
```

Features:
- Hashable like a tuple.  It returns a hash if and only if its values are hashable.
- Works with both Python 2 and Python3.
- Supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is created with the same arguments that instantiate a regular dict.

Speed:
- Lookup times are O(1)
- Just as fast as regular dictionaries.  40 - 60 nanoseconds per lookup.
- Designed to store keyword arguments for memoized function calls.
- 40% Faster to compare two FrozenDicts than two corresponding frozensets.

Memory:
- Uses 50-60 more bytes than would be required with a regular dictionary.

Hash Algorithm:
- Hashes a frozenset of the dictionary items
- The hash calculation is deferred until needed and then cached, like a string.

Recursion:
- A frozen dict is not recursive by default, but an auxilary function "freeze" does do it.
- "freeze" turns unhashable objects into generic python immutable types
- sequences such as lists become tuples
- unordered collections such as sets become frozenset
- mappings such as dictionaries become FrozenDict instances
