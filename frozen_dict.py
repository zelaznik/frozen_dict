def enclose(func):
	return func()
		
@enclose
def FrozenDict():
	#We have to enclose this method in the class definition
	#because we are overriding both __iter__ and __getitem__
	g = tuple.__getitem__
	class FrozenDict(tuple):
		__slots__ = ()
		def __new__(cls, *args, **kw):
			#Define a regular dictionary first
			#Define an arbitrary ordering if keys
			#Map the key-value pairs in the same order
			#Create a dict which returns the position of the item
			#save only the __getitem__ method of that dict
			#then delete the original dictionary
			#If there's a way to modify the dictionary, 
			#then it's damn near impossible.
			d = dict(*args, **kw)
			keys = tuple(d)
			items = tuple([(k,d[k]) for k in keys])
			lkp = {k:i for i,k in enumerate(keys)}
			idx = lkp.__getitem__
			del lkp, keys, d
			return tuple.__new__(cls,(items,idx))

		def __iter__(self):
			return self.keys()
			
		def __contains__(self, key):
			try:
				g(self,1)(key)
			except KeyError:
				return False
			else:
				return True
			
		def __repr__(self):
			cls = type(self).__name__
			_repr = repr(dict(g(self,0)))
			return '%s(%s)' % (cls,_repr)
			
		def __getitem__(self, key):
			i = g(self,1)(key)
			return g(self,0)[i][1]

		def __len__(self):
			return len(g(self,0))
			
		def __hash__(self):
			f = frozenset(g(self,0))
			return hash(f)
			
		def __eq__(self, other):
			return dict(self) == other
			
		def __ne__(self, other):
			return dict(self) != other

		def copy(self):
			return type(self)(self)
		
		def keys(self):
			for key, value in g(self,0):
				yield key
				
		def values(self):
			for key, value in g(self,0):
				yield value
				
		def items(self):
			for item in g(self,0):
				yield item
				
		def get(self, key):
			try:
				return self[key]
			except KeyError:
				return None

		# "count" and "index" are built in to 'tuple', so we
		# we may as well override them into something useful.
		def count(self, value):
			return list(self.values()).count(value)
			
		def index(self, key):
			return g(self,1)(key)

	return FrozenDict
