Summary:
- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- Most implementations of FrozenDict simply subclass dict, or place a thin wrapper around a dict.
- This implemtation is 100% thread safe.  It subclasses tuple.
- All of the key-value pairs are stored inside either tuples or frozensets.

Features:
- Hashable like a tuple.  It returns a hash if and only if its values are hashable.
- Compatible with both Python 2 and Python3.
- Supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is also created using the same arguments needed to instantiate a regular dict. 
- Can replace an existing dictionary, assuming your code doesn't check types.

Speed:
- Uses similar hash-table lookup methodology as a dict, but done in pure Python.
- Lookup times are on O(1).  Using strings as keys, 1.69 micro-sec for a dict with 3 items.
- For a dictionary with 1 million itmes, it takes on average 2.51 micro-sec to retrieve a value.

Requirements:
- Python 2.6 or later, any version of Python3.
- Unit tested on 2.7 and 3.4

Python2 vs Python3:
- The same differences that are found in regular dictionaries.
- keys(), values(), and items() in Python3 return generators.
- keys(), values(), and items() in Python2 return lists.
- iterkeys(), itervalues(), and iteritems() do not exist in Python3.

Not Implemented Features:
- Python3: None
- Python2: viewkeys, viewvalues, and viewitems
- These are legacy methods from Python2, discontinued in Python3.
- Those methods would require creating a new dict every time.
- If you want those methods, either modify my code or create your own subclass.

Methodology:
- A FrozenDict is a subclass of tuple, and it contains two main entries
- One entry is a tuple of the items sorted by hash, the other is a lookup table of those hashes.
- To get an item, the key is hashed, python's "bisect" finds the index of the hash.
- During a hash collision, items are stored inside a subclass of frozenset, "Group".
- Group can accept unhashable items, but will then no longer return a hash itself.
- Equality is tested by converting the other object into a FrozenDict.
- The hash of a FrozenDict is calculated by simply hashing the tuple which stores all the items.
