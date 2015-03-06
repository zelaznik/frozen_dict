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

    def add_unit(self, items = {}, **kw):
        ''' Each unit contains a reulgar dictionary (orig),
            its frozen counterpart (frz), a regular dictionary
            derived from the frozen one (thaw)
            and a regular dictionary with one additional item (pl).'''
        orig = dict(items, **kw)
        frz = FrozenDict(items, **kw)
        thaw = dict(frz)
        aggKey, aggValue, p1 = self.plus_one(orig)
        u = frz_nt(orig,frz,p1,thaw,aggKey,aggValue)
        self.units.append(u)

        #Add a second version with addition items that have hash collisions
        orig = orig.copy()
        coll = {hash(k): (k,v) for k,v in orig.items()}
        orig.update(coll)
        frz = FrozenDict(orig)
        thaw = dict(frz)
        aggKey, aggValue, p1 = self.plus_one(orig)
        u = frz_nt(orig,frz,p1,thaw,aggKey,aggValue)
        self.units.append(u)

        #Add a third version with addition items that have hash collisions
        #but one in which one of the values included in the hash collision
        #itself is unhashable.
        orig = orig.copy()
        coll = {hash(k): (k,v) for k,v in orig.items()}
        for k in coll:
            coll[k] = []
            break
        orig.update(coll)
        frz = FrozenDict(orig)
        thaw = dict(frz)
        aggKey, aggValue, p1 = self.plus_one(orig)
        u = frz_nt(orig,frz,p1,thaw,aggKey,aggValue)
        self.units.append(u)

        #Add a fourth version which includes an unorderable item
        orig = orig.copy()
        coll = {hash(k): (k,v) for k,v in orig.items()}
        for k in coll:
            coll[k] = object()
            break
        orig.update(coll)
        frz = FrozenDict(orig)
        thaw = dict(frz)
        aggKey, aggValue, p1 = self.plus_one(orig)
        u = frz_nt(orig,frz,p1,thaw,aggKey,aggValue)
        self.units.append(u)


    def setUp(self):
        self.item_recursion_max = 10
        self.units = []
        self.add_unit()
        self.add_unit({})
        self.add_unit({-1: 'NegOne', -2: 'NegTwo'})     #Minus one hashes to -2, '' hashes to 0
        self.add_unit({-1: ['NegOne'], -2: ['NegTwo']}) #so these are induced hash collisions
        self.add_unit({'': 'empty', 0: 'Zero'})
        self.add_unit({'': ['empty'], 0: ['Zero']})
        
        self.add_unit(x=1)
        self.add_unit({'x': 1})

        self.add_unit(x=3,y=4)
        self.add_unit(x=3,y=4,z=5)
        self.add_unit({'x': 3,'y': 4,'z': 5})
        self.add_unit(a=3,b=4,c=0)
        self.add_unit({'a': 3,'b': 4,'c': 0})

        self.add_unit({'my_list': []})
        self.add_unit(my_list = [])

        self.add_unit(my_list = [], my_object = object())
        self.add_unit({'my_list': [], 'my_object': object()})
        
        self.units = tuple(self.units)
        
    def tearDown(self):
        del self.units
    
    def test_frozendict_reversible(self):
        for u in self.units:
            self.assertEqual(u.thaw, u.orig)
            f = FrozenDict(u.thaw)
            try:
                s = {f,u.frz}
            except TypeError:
                continue
            self.assertEqual(len(s), 1)
        
    def test_frozendict_operator__repr__(self):
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

    def test_frozendict_operator__eq__(self):
        for u in self.units:
            self.assertEqual(u.orig, u.thaw)
            self.assertEqual(u.thaw, u.orig)
            
            self.assertNotEqual(u.plus_one, u.thaw)
            self.assertNotEqual(u.thaw, u.plus_one)
            
            t = tuple(u.frz.items())
            self.assertNotEqual((u.frz == t), True)
            self.assertNotEqual((t == u.frz), True)
            try:
                f = frozenset(u.frz.items())
            except TypeError:
                pass
            else:
                self.assertNotEqual((u.frz == f), True)
                self.assertNotEqual((f == u.frz), True)

            for a in self.units:
                orig_eq = (u.orig == a.orig)
                self.assertEqual((u.frz == a.frz), orig_eq)
                self.assertEqual((a.frz == u.frz), orig_eq)
                self.assertEqual((u.orig == a.frz), orig_eq)
                self.assertEqual((a.frz == u.orig), orig_eq)
                self.assertEqual((u.frz == a.orig), orig_eq)
                self.assertEqual((a.orig == u.frz), orig_eq)
            
    def test_frozendict_operator__ne__(self):
        for u in self.units:
            self.assertEqual((u.orig != u.thaw), False)
            self.assertEqual((u.thaw != u.orig), False)
            self.assertEqual((u.plus_one != u.thaw), True)
            self.assertEqual((u.thaw != u.plus_one), True)
            for a in self.units:
                ne_orig = u.orig != a.orig
                self.assertEqual((u.frz != a.frz), ne_orig)
                self.assertEqual((a.frz != u.frz), ne_orig)
            
    def test_frozendict_operator__len__(self):
        for u in self.units:
            self.assertEqual(len(u.orig),len(u.frz))
            self.assertNotEqual(len(u.plus_one),len(u.frz))
            
    def test_frozendict_operator__iter__(self):
        for u in self.units:
            self.assertEqual(set(iter(u.orig)),set(iter(u.frz)))
            self.assertNotEqual(set(iter(u.plus_one)),set(iter(u.frz)))

    def test_frozendict_operator__getitem__(self):
        for u in self.units:
            for k,v in u.orig.items():
                self.assertEqual(u.frz[k], v)
            self.assertRaises(KeyError,u.frz.__getitem__,u.aggKey)

    def test_frozendict_operator__bool__(self):
        for u in self.units:
            assert (bool(u.orig) == bool(u.frz))
            
    def test_frozendict_operator__hash__(self):
        for u in self.units:
            try:
                hash(tuple(u.orig.values()))
                h = True
            except TypeError:
                h = False
            if h:
                self.assertEqual({u.frz}, {u.frz, FrozenDict(u.orig.items())})
                self.assertNotEqual({u.frz}, {u.frz, FrozenDict(u.plus_one.items())})
            else:
                s = set()
                self.assertRaises(TypeError, s.add, u.frz)

    def test_frozendict_behavior_inside_a_set(self):
        for u in self.units:
            for a in self.units:
                try:
                    s = {u.frz, a.frz}
                except TypeError:
                    s = None
                if not s:
                    self.assertEqual((u.orig == a.orig), (u.frz == a.frz))
                else:
                    f = frozenset
                    t = set([f(u.frz.items()), f(a.frz.items())])
                    self.assertEqual(len(s), len(t))

    def test_frozendict_operator__contains__(self):
        for u in self.units:
            for key in u.orig:
                self.assertIn(key,u.frz)
            self.assertNotIn(u.aggKey,u.frz)
            
    def test_frozendict_method_fromkeys(self):
        for u in self.units:
            f = u.frz.fromkeys(tuple(u.frz), u.aggValue)
            d = u.orig.fromkeys(tuple(u.orig), u.aggValue)
            self.assertIs(type(f), type(u.frz))
            self.assertEqual(f, d)

    def test_frozendict_method_get(self):
        for alt in (None, 'alt0','alt1'):
            for u in self.units:
                for k,v in u.orig.items():
                    self.assertEqual(u.frz.get(k), v)
                self.assertEqual(u.frz.get(u.aggKey, alt), alt)

    def test_frozendict_method_copy(self):
        for u in self.units:
            fCopy = u.frz.copy()
            self.assertEqual(dict(fCopy), u.orig)
            self.assertEqual(fCopy, u.frz)
            self.assertIsNot(fCopy, u.frz)
            self.assertIs(type(fCopy), type(u.frz))
            try:
                hash(u.frz)
            except TypeError:
                continue
            self.assertEqual({u.frz}, {u.frz, fCopy})
            
    def test_frozendict_generator_consistency(self):
        #Make sure the keys/values/and items all yield their results
        #in orders that are consistent with each other.
        #frz[list(frz.keys())[x]] == frz[list(frz.values())][x]
        #for all 0 <= x <= len(frz)
        for u in self.units:
            zipped = zip(u.frz.keys(), u.frz.values(), u.frz.items())
            for key, value, item in zipped:
                self.assertEqual(item, (key, value))

    def test_frozendict_fails_operator__setitem__(self):
        def func(obj, key, value):
            obj[key] = value
        for u in self.units:
            self.assertRaises(TypeError,func,u.frz,u.aggKey,u.aggValue)
            
    def test_frozendict_fails_operator__delitem__(self):
        def func(obj, key):
            del obj[key]
        for u in self.units:
            for key in u.frz:
                self.assertRaises(TypeError,func,u.frz,key)
                
    def test_frozendict_method__new__(self):
        def test(**kw):
            pass
        for u in self.units:
            try:
                test(**u.orig)
            except TypeError:
                continue
            
            xx = FrozenDict(**u.orig)
            self.assertEqual(u.orig, dict(xx))
            
            yy = FrozenDict(u.orig)
            self.assertEqual(u.orig, dict(yy))
            
            xy = FrozenDict(u.orig, **u.orig)
            self.assertEqual(u.orig, dict(xy))

            if not u.orig:
                continue

            cls = FrozenDict
            fcn = cls.__new__
            kw = {tuple(u.orig)[0]: u.aggValue}
            self.assertRaises(ValueError, fcn, cls, u.orig, **kw)
            
            keys = tuple(u.orig)
            if set(map(type, keys)) != {str}:
                continue
            for i in range(len(keys)):
                items  = {k: u.orig[k] for k in keys[:i]}
                kwargs = {k: u.orig[k] for k in keys[i:]}
                agg = FrozenDict(items, **kwargs)
                rev = FrozenDict(kwargs, **items)
                self.assertEqual(agg, rev)
                self.assertEqual(agg, u.frz)
                self.assertEqual(rev, u.frz)
                self.assertEqual(dict(agg), dict(rev))

                
    def test_frozendict_fails_method_clear(self):
        def func(obj):
            obj.clear()
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz)
            
    def test_frozendict_fails_method_update(self):
        def func(obj, other):
            obj.update(other)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,{u.aggKey:u.aggValue})
            
    def test_frozendict_fails_method_pop(self):
        def func(obj, key):
            return obj.pop(key)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,u.aggKey)
            
    def test_frozendict_fails_method_popitem(self):
        def func(obj):
            return obj.popitem()
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz)

    def test_frozendict_fails_method_setdefault(self):
        def func(obj, val):
            obj.setdefault(val)
        for u in self.units:
            self.assertRaises(AttributeError,func,u.frz,u.aggKey)
            
    def test_frozendict_fails_dict_operator__setitem__(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.__setitem__, u.frz, u.aggKey, u.aggValue)

    def test_frozendict_fails_dict_operator__delitem__(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.__delitem__, u.frz, u.aggKey, u.aggValue)

    def test_frozendict_fails_dict_method_pop(self):
        for u in self.units:
            for key in u.frz.keys():
                self.assertRaises(TypeError, dict.pop, u.frz, key)
    
    def test_frozendict_fails_dict_method_popitem(self):
        for u in self.units:
            for key in u.frz.keys():
                self.assertRaises(TypeError, dict.popitem, u.frz)
                
    def test_frozendict_fails_dict_method_setdefaults(self):
        for u in self.units:
            self.assertRaises(TypeError, dict.setdefault, u.frz, u.aggKey)

    @staticmethod
    def __hash_sorter(dct):
        f = lambda i: hash(i[0])
        items = dct.items()
        items = sorted(items, key=f)
        lkp = {}
        for i, (k,v) in enumerate(items):
            lkp[('keys',k)] = i
            lkp[('values',v)] = i
            lkp[('items',(k,v))] = i
        return lkp

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
            
    def test_frozendict_same_as_regular_dict_sorted_keys(self):
        self.__test_same_as_regular_dict_sorted_methods('keys')

    def test_frozendict_same_as_regular_dict_sorted_values(self):
        self.__test_same_as_regular_dict_sorted_methods('values')

    def test_frozendict_same_as_regular_dict_sorted_items(self):
        self.__test_same_as_regular_dict_sorted_methods('items')

    
if version == 2:
    class Test_FrozenDict_Python2(Test_FrozenDict):
        def test_frozendict_Python2_lists_keys(self):
            for u in self.units:
                self.assertEqual(list(u.frz.keys()), u.frz.keys())

        def test_frozendict_Python2_lists_values(self):
            for u in self.units:
                self.assertEqual(list(u.frz.values()), u.frz.values())

        def test_frozendict_Python2_lists_items(self):
            for u in self.units:
                self.assertEqual(list(u.frz.items()), u.frz.items())
    
        @staticmethod
        def iterfunc(method):
            return len(method())

        def test_frozendict_Python2_generators_iterkeys(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.iterkeys)
    
        def test_frozendict_Python2_generators_itervalues(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.itervalues)

        def test_frozendict_Python2_generators_iteritems(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.iteritems)
    
if version == 3:
    class Test_FrozenDict_Python3(Test_FrozenDict):
        @staticmethod
        def iterfunc(method):
            return len(method())

        def test_frozendict_Python3_generators_keys(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.keys)
        
        def test_frozendict_Python3_generators_values(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.values)

        def test_frozendict_Python3_generators_items(self):
            for u in self.units:
                self.assertRaises(TypeError,self.iterfunc,u.frz.items)

del Test_FrozenDict
if __name__ == '__main__':
    unittest.main()
