from frozen_dict import FrozenDict
import unittest
from collections import namedtuple

frz_nt = namedtuple('FrozenDictTestUnit',('orig','frz','plus_one','thaw','aggKey','aggValue'))

class Test_FrozenDict(unittest.TestCase):
	@staticmethod
	def plus_one(orig):
		aggKey = tuple(orig.keys())
		aggValue = tuple(orig.values())
		plus_one = dict(orig)
		plus_one[aggKey] = aggValue
		plus_one = type(orig)(plus_one)
		return aggKey, aggValue, plus_one

	def add_unit(self, *args, **kw):
		orig = dict(*args, **kw)
		frz = FrozenDict(*args, **kw)
		aggKey, aggValue, p1 = self.plus_one(orig)
		thaw = dict(orig)
		u = frz_nt(orig,frz,p1,thaw,aggKey,aggValue)
		self.units.append(u)

	def setUp(self):
		self.units = []
		self.add_unit()
		self.add_unit({})
		self.add_unit(x=1)
		self.add_unit({'x': 1})
		self.add_unit(x=3,y=4,z=5)
		self.add_unit({'x': 3,'y': 4,'z': 5})
		self.add_unit({'my_list': []})
		self.add_unit(my_list = [])

	def test_operator__eq__(self):
		for u in self.units:
			self.assertEqual((u.orig == u.thaw), True)
			self.assertEqual((u.plus_one == u.thaw), False)
			
	def test_operator__ne__(self):
		for u in self.units:
			self.assertEqual((u.orig != u.thaw), False)
			self.assertEqual((u.plus_one != u.thaw), True)
			
	def test_operator__len__(self):
		for u in self.units:
			self.assertEqual(len(u.orig),len(u.frz))
			self.assertNotEqual(len(u.plus_one),len(u.frz))
			
	def test_operator__iter__(self):
		for u in self.units:
			self.assertEqual(set(u.orig),set(u.frz))
			self.assertNotEqual(set(u.plus_one),set(u.frz))

	def test_operator__getitem__(self):
		for u in self.units:
			for k,v in u.orig.items():
				self.assertEqual(u.frz[k], v)
			self.assertRaises(KeyError,u.frz.__getitem__,u.aggKey)

	def test_operator__bool__(self):
		for u in self.units:
			assert (bool(u.orig) == bool(u.frz))
			
	def test_operator__hash__(self):
		for u in self.units:
			try:
				h = hash(tuple(u.orig.values()))
			except TypeError:
				continue
			self.assertEqual(hash(u.frz), hash(frozenset(u.orig.items())))
			self.assertNotEqual(hash(u.frz), hash(frozenset(u.plus_one.items())))
			self.assertEqual({u.frz}, {u.frz, FrozenDict(u.orig.items())})
			self.assertNotEqual({u.frz}, {u.frz, FrozenDict(u.plus_one.items())})

	def test_operator__contains__(self):
		for u in self.units:
			for key in u.orig:
				self.assertIn(key,u.frz)
			self.assertNotIn(u.aggKey,u.frz)				

	def test_method_get(self):
		for u in self.units:
			for k,v in u.orig.items():
				self.assertEqual(u.frz.get(k), v)
			self.assertEqual(u.frz.get(u.aggKey), None)
			
	def test_method_count(self):
		for u in self.units:
			vals = list(u.orig.values())
			for v in vals:
				self.assertEqual(vals.count(v), u.frz.count(v))
			
	def test_generator_consistency(self):
		for u in self.units:
			for key, value, item in zip(u.frz.keys(), u.frz.values(), u.frz.items()):
				self.assertEqual(item, (key, value))
				self.assertIn(key, u.frz)
			self.assertEqual((u.aggKey in u.frz), (u.aggKey in u.orig))
			
	def test_fails_operator__setitem__(self):
		def func(obj, key, value):
			obj[key] = value
		for u in self.units:
			self.assertRaises(TypeError,func,u.frz,u.aggKey,u.aggValue)
			
	def test_fails_operator__delitem__(self):
		def func(obj, key):
			del obj[key]
		for u in self.units:
			for key in u.frz:
				self.assertRaises(TypeError,func,u.frz,key)
				
	def test_fails_method_clear(self):
		def func(obj):
			obj.clear()
		for u in self.units:
			self.assertRaises(AttributeError,func,u.frz)
			
	def tests_fails_method_update(self):
		def func(obj, other):
			obj.update(other)
		for u in self.units:
			self.assertRaises(AttributeError,func,u.frz,{u.aggKey:u.aggValue})

	def test_fails_dictionary_methods(self):
		for u in self.units:
			self.assertRaises(TypeError, dict.__setitem__, u.frz, u.aggKey, u.aggValue)
			self.assertRaises(TypeError, dict.__delitem__, u.frz, u.aggKey, u.aggValue)
			self.assertRaises(TypeError, dict.update, u.frz, {u.aggKey: u.aggValue})
			
	def test_results_are_generators(self):
		def func(method):
			return len(method())
		for u in self.units:
			for method_name in ('keys','values','items'):
				method = getattr(u.frz, method_name)
				self.assertRaises(TypeError,func,method)

	def test_sorted_keys(self):
		for u in self.units:
			self.assertEqual(sorted(u.orig.keys()),sorted(u.frz.keys()))
	
	def test_sorted_values(self):
		for u in self.units:
			self.assertEqual(sorted(u.orig.values()),sorted(u.frz.values()))
	
	def test_sorted_items(self):
		for u in self.units:
			self.assertEqual(sorted(u.orig.items()),sorted(u.frz.items()))

if __name__ == '__main__':
	unittest.main()
