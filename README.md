Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
A FrozenDict is a subclass of tuple, and it contains two main entries.
One entry is a tuple of all the items sorted by hash value.
The other entry is a lookup table of those hashes.
A FrozenDict is like a tuple.  It's hashable if and only if its values are hashable.
