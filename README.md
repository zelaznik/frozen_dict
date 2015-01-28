- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- A FrozenDict is a subclass of tuple, and it contains two main entries.
- One entry is a tuple of all the items sorted by hash value.
- The other entry is a lookup table of those hashes.

- A FrozenDict is like a tuple.  It's hashable if and only if its values are hashable.
- A FrozenDict supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is also created using the same arguments needed to instantiate a regular dict.
- Lookup times are on O(1).  Using strings as keys, 1.69 micro-sec for a dict with 3 items.
- For a dictionary with 1 million itmes, it takes on average 2.51 micro-sec to retrieve a value.

- Dictionary read-only features that are NOT implemented: viewkeys, viewvalues, and viewitems
- These are legacy methods from Pyton2, discontinued in Python3.
- Those methods would require creating a new dict every time.
- If you want those methods, either modify my code or create your own subclass.

