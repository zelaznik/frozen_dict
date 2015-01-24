from frozen_dict import FrozenDict
import unittest
from collections import namedtuple

frz_nt = namedtuple('FrozenDictTestUnit',('orig','frz','plus_one','thaw','aggKey','aggValue'))

if 3 / 2 == 1:
    version = 2
elif 3 / 2 == 1.5:
    version = 3

class Test_FrozenDict(unittest.TestCase):
    @staticmethod
    def plus_one(orig):
        #Plus one is the original dictionary with one extra item
        #that by definition cannot be contained in the original
        #aggKey is the collection of all original keys.
        #aggValue is the collection of all original values.
        aggKey = tuple(orig.keys())
        aggValue = tuple(orig.values())
        plus_one = dict(orig)
        plus_one[aggKey] = aggValue
        plus_one = type(orig)(plus_one)
        return aggKey, aggValue, plus_one

    def add_unit(self, *args, **kw):
        ''' Each unit contains a reulgar dictionary (orig),
            its frozen counterpart (frz), a regular dictionary
            derived from the frozen one (thaw)
            and a regular dictionary with one additional item (pl).'''
        orig = dict(*args, **kw)
        frz = FrozenDict(*args, **kw)
        thaw = dict(frz)
        aggKey, aggValue, p1 = self.plus_one(orig)
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
        self.add_unit(my_list = [], my_object = object())
        self.add_unit({'my_list': [], 'my_object': object()})
        
    def test_frozendict_reversible(self):
        for u in self.units:
            self.assertEqual(u.thaw, u.orig)                
            f = FrozenDict(u.thaw)
            try:
                s = {f,u.frz}
            except TypeError:
                continue
            self.assertEqual(len(s), 1)
        
    def test_operator__repr__(self):
        #In many cases eval(repr(obj)) == obj
        #We're testing that if the above equality holds for dict,
        #that it also holds for FrozenDict
        def func(obj):
            try:
                return obj == eval(repr(obj))
            except Exception:
                return False
        for u in self.units:
            self.assertEqual(func(u.frz), func(u.orig))

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
            
    def test_method_fromkeys(self):
        for u in self.units:
            f = u.frz.fromkeys(tuple(u.frz), u.aggValue)
            d = u.orig.fromkeys(tuple(u.orig), u.aggValue)
            self.assertIs(type(f), type(u.frz))
            self.assertEqual(f, d)

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
        #Make sure the keys/values/and items all yield their results
        #in orders that are consistent with each other.
        #frz[list(frz.keys())[x]] == frz[list(frz.values())][x]
        #for all 0 <= x <= len(frz)
        for u in self.units:
            zipped = zip(u.frz.keys(), u.frz.values(), u.frz.items())
            for key, value, item in zipped:
                self.assertEqual(item, (key, value))

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
            
    def test_fails_method_update(self):
        def func(obj, other):
            obj.update(other)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,{u.aggKey:u.aggValue})
            
    def test_fails_method_pop(self):
        def func(obj, key):
            return obj.pop(key)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,u.aggKey)
            
    def test_fails_method_popitem(self):
        def func(obj):
            return obj.popitem()
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz)

    def test_fails_method_setdefault(self):
        def func(obj, val):
            obj.setdefault(val)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,u.aggKey)
            
    def test_fails_dict_operator__setitem__(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.__setitem__, u.frz, u.aggKey, u.aggValue)

    def test_fails_dict_operator__delitem__(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.__delitem__, u.frz, u.aggKey, u.aggValue)

    def test_fails_dict_method_pop(self):
        for u in self.units:
            for key in u.frz.keys():
                self.assertRaises(TypeError, dict.pop, u.frz, key)
    
    def test_fails_dict_method_popitem(self):
        for u in self.units:
            for key in u.frz.keys():
                self.assertRaises(TypeError, dict.popitem, u.frz)
                
    def test_fails_dict_method_setdefauls(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.setdefault, u.frz, u.aggKey)

    def __test_same_as_regular_dict_sorted_methods(self, method_name):
        for u in self.units:
            try:
                method = getattr(u.orig, method_name)
                s = sorted(method())
            except TypeError:
                continue
            else:
                method = getattr(u.frz, method_name)
                f = sorted(method())
            self.assertEqual(s,f)
            
    def test_same_as_regular_dict_sorted_keys(self):
        self.__test_same_as_regular_dict_sorted_methods('keys')

    def test_same_as_regular_dict_sorted_values(self):
        self.__test_same_as_regular_dict_sorted_methods('values')

    def test_same_as_regular_dict_sorted_items(self):
        self.__test_same_as_regular_dict_sorted_methods('items')

    
if version == 2:
    def test_Python2_operator__gt__(self):
        for u in self.units:
            for a in self.units:
                xx = u.orig > a.orig
                xy = u.frz > a.orig
                yx = u.orig > a.frz
                yy = u.frz > a.frz
                s = {xx,xy,yx,yy}
                self.assertEqual(len(s), 1)
    Test_FrozenDict.test_Python2_operator__gt__ = test_Python2_operator__gt__
                
    def test_Python2_operator__ge__(self):
        for u in self.units:
            for a in self.units:
                xx = u.orig >= a.orig
                xy = u.frz >= a.orig
                yx = u.orig >= a.frz
                yy = u.frz >= a.frz
                s = {xx,xy,yx,yy}
                self.assertEqual(len(s), 1)
    Test_FrozenDict.test_Python2_operator__ge__ = test_Python2_operator__ge__

    def test_Python2_operator__le__(self):
        for u in self.units:
            for a in self.units:
                xx = u.orig <= a.orig
                xy = u.frz <= a.orig
                yx = u.orig <= a.frz
                yy = u.frz <= a.frz
                s = {xx,xy,yx,yy}
                self.assertEqual(len(s), 1)
    Test_FrozenDict.test_Python2_operator__le__ = test_Python2_operator__le__

    def test_Python2_operator__lt__(self):
        for u in self.units:
            for a in self.units:
                xx = u.orig < a.orig
                xy = u.frz < a.orig
                yx = u.orig < a.frz
                yy = u.frz < a.frz
                s = {xx,xy,yx,yy}
                self.assertEqual(len(s), 1)
    Test_FrozenDict.test_Python2_operator__lt__ = test_Python2_operator__lt__

    def test_Python2_lists_keys(self):
        for u in self.units:
            self.assertEqual(list(u.frz.keys()), u.frz.keys())
    Test_FrozenDict.test_Python2_lists_keys = test_Python2_lists_keys

    def test_Python2_lists_values(self):
        for u in self.units:
            self.assertEqual(list(u.frz.values()), u.frz.values())
    Test_FrozenDict.test_Python2_lists_values = test_Python2_lists_values

    def test_Python2_lists_items(self):
        for u in self.units:
            self.assertEqual(list(u.frz.items()), u.frz.items())
    Test_FrozenDict.test_Python2_lists_items = test_Python2_lists_items
    
    @staticmethod
    def iterfunc(method):
        return len(method())
    Test_FrozenDict.iterfunc = iterfunc

    def test_Python2_generators_iterkeys(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.iterkeys)
    Test_FrozenDict.test_Python2_generators_iterkeys = test_Python2_generators_iterkeys
    
    def test_Python2_generators_itervalues(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.itervalues)
    Test_FrozenDict.test_Python2_generators_itervalues = test_Python2_generators_itervalues

    def test_Python2_generators_iteritems(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.iteritems)
    Test_FrozenDict.test_Python2_generators_iteritems = test_Python2_generators_iteritems
    
    def test_Python2_viewkeys(self):
        for u in self.units:
            vv = 'dict_keys(%r)' % u.frz.keys()
            self.assertEqual(vv, repr(u.frz.viewkeys()))
    Test_FrozenDict.test_Python2_viewkeys = test_Python2_viewkeys
        
    def test_Python2_viewvalues(self):
        for u in self.units:
            vv = 'dict_values(%r)' % u.frz.values()
            self.assertEqual(vv, repr(u.frz.viewvalues()))
    Test_FrozenDict.test_Python2_viewvalues = test_Python2_viewvalues

    def test_Python2_viewitems(self):
        for u in self.units:
            vv = 'dict_items(%r)' % u.frz.items()
            self.assertEqual(vv, repr(u.frz.viewitems()))
    Test_FrozenDict.test_Python2_viewitems = test_Python2_viewitems

    def test_Python2_operator__cmp__(self):
        for u in self.units:
            for a in self.units:
                xx = cmp(u.orig, a.orig)
                xy = cmp(u.frz, a.orig)
                yx = cmp(u.orig, a.frz)
                yy = cmp(u.frz, a.frz)
                s = {xx,xy,yx,yy}
                self.assertEqual(len(s), 1)
    Test_FrozenDict.test_Python2_operator__cmp__ = test_Python2_operator__cmp__    
                
    
if version == 3:
    @staticmethod
    def iterfunc(method):
        return len(method())
    Test_FrozenDict.iterfunc = iterfunc

    def test_Python3_generators_keys(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.keys)
    Test_FrozenDict.test_Python3_generators_keys = test_Python3_generators_keys
    
    def test_Python3_generators_values(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.values)
    Test_FrozenDict.test_Python3_generators_values = test_Python3_generators_values

    def test_Python3_generators_items(self):
        for u in self.units:
            self.assertRaises(TypeError,self.iterfunc,u.frz.items)
    Test_FrozenDict.test_Python3_generators_items = test_Python3_generators_items

if __name__ == '__main__':
    unittest.main()