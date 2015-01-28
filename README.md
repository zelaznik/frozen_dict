Features:
- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- Hashable like a tuple.  It returns a hash if and only if its values are hashable.
- Compatible with both Python 2 and Python3.  Tested on 2.7 and 3.4
- Supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is also created using the same arguments needed to instantiate a regular dict. 
- Can be dropped into code in place of an existing dictionary.
- Lookup times are on O(1).  Using strings as keys, 1.69 micro-sec for a dict with 3 items.
- For a dictionary with 1 million itmes, it takes on average 2.51 micro-sec to retrieve a value.

-Not Implemented Features:
- Python3: None
- Python2: viewkeys, viewvalues, and viewitems
- These are legacy methods from Python2, discontinued in Python3.
- Those methods would require creating a new dict every time.
- If you want those methods, either modify my code or create your own subclass.

-Methodology:
- A FrozenDict is a subclass of tuple, and it contains two main entries.
- One entry is a tuple of all the items sorted by hash value, the other entry is a lookup table of those hashes.
- In the event of a hash collision, items are stored inside a special subclass of frozenset
- The frozenset can accept key-value pairs with unhashable items, but will then not return a hash if that happens.
- Equality between a FrozenDict and another object is tested by converting the other object into a FrozenDict first.
- The hash of a FrozenDict is simply the hash of the tuple which stores all the sorted items.  (As well as the occasional frozenset).
