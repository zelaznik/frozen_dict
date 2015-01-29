Summary:
- Behaves in most ways like a regular dictionary, except that it's immutable, TRULY immutable.
- Most implementations of FrozenDict simply subclass dict, or wrap a thin object around one.
- This implemtation is 100% thread safe.  It subclasses tuple.
- All bindings, other than the items themselves, are subclasses of tuple or frozenset.

Features:
- Hashable like a tuple.  It returns a hash if and only if its values are hashable.
- Works with both Python 2 and Python3.
- Supports bi-directional conversion to and from regular dictionaries
- A FrozenDict is created with the same arguments that instantiate a regular dict. 
- Can replace an existing dictionary, assuming your code doesn't check types.
- Great for debugging.

Speed:
- Uses sorted arrays, operattions are O(log(n)).
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
- Python2: viewkeys, viewvalues, and viewitems
- These are legacy methods from Python2, discontinued in Python3.
- Those methods would require creating a new dict every time.
- If you want those methods, either modify my code or create your own subclass.

Methodology:
- A FrozenDict is a subclass of tuple, and it contains two main entries:
- One entry is a tuple of the items sorted by hash, the other is a lookup table of those hashes.
- Items, meaning key-value pairs, are grouped by their key's hash value.
- Most items have their own unique hash.  Approx 1 in 1400 items have collisions.
- To return an value, the key is hashed, python's "bisect" finds the hash's location.
- The second entry holds all of the hash-groups, and it is promptly retrieved.

Resolving Hash Collisions
- During a collision, items are placed in a subclass of frozenset, called "Group".
- "Group" can accept unhashable items, but will then no longer return a hash itself.
- Each key-value pair is put in a class "Item" which only hashes the key.
- This allows items with un-hashable values to be stored inside an unordered frozenset.
- When hashing "Group", we unpack the items into regular tuples.
- Then we put those items into a new frozenset and take that hash.
- If any item is unhashable, this is where we'll get an error.
