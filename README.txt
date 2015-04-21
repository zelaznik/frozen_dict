Summary:
    Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
    Most implementations of FrozenDict simply subclass dict, or wrap a thin object around one.
    This implemtation does the wrapping at the C level, making it impossible to change from Python.

Features:
    Hashable like a tuple. It returns a hash if and only if its values are hashable.
    Works with both Python 2 and Python3.
    Supports bi-directional conversion to and from regular dictionaries
    A FrozenDict is created with the same arguments that instantiate a regular dict.
    Great for debugging.

Speed:
    Just as fast as regular dictionaries. 40 - 60 nanoseconds per lookup.
    Lookup times are O(1)

Memory:
    Uses 50-60 more bytes than would be required with a regular dictionary.
