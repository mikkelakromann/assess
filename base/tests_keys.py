from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.keys import Keys

class KeysTestCase(TestCase):
    """Testing Keys()."""
    
    def setUp(self):
        v = Version()
        v.save()
        TestItemA.objects.create(label='a1',version_first=v)
        TestItemA.objects.create(label='a2',version_first=v)
        TestItemB.objects.create(label='b1',version_first=v)
        TestItemB.objects.create(label='b2',version_first=v,version_last=v)
        TestItemC.objects.create(label='c1',version_first=v)
        TestItemC.objects.create(label='c2',version_first=v)
        

    def test_key_headers_data(self):
        """Testing the AssessData meta model's interaction with Keys()."""

        # Single column table (column_field = an index field)
        keys_data = Keys(TestData)
        keys_data.set_headers('value')
        self.assertEqual(keys_data.column_field,'value')
        self.assertEqual(keys_data.table_one_column,True)
        self.assertEqual(keys_data.index_headers,['testitema','testitemb','testitemc'])
        self.assertEqual(keys_data.value_headers,['value'])

        # Multi-column table (column_field = value_field)
        keys_data = Keys(TestData)
        keys_data.set_headers('testitemc')
        self.assertEqual(keys_data.column_field,'testitemc')
        self.assertEqual(keys_data.table_one_column,False)
        self.assertEqual(keys_data.index_headers,['testitema','testitemb'])
        self.assertEqual(keys_data.value_headers,['c1','c2'])

        # Multi-column table, alt. column (column_field = value_field)
        keys_data = Keys(TestData)
        keys_data.set_headers('testitemb')
        self.assertEqual(keys_data.column_field,'testitemb')
        self.assertEqual(keys_data.table_one_column,False)
        self.assertEqual(keys_data.index_headers,['testitema','testitemc'])
        self.assertEqual(keys_data.value_headers,['b1'])


    def test_key_get_key_list_data(self):
        """Testing key combos for Keys() row keys, data_model."""
        
        keys_data = Keys(TestData)
        keys_data.set_headers('value')
        key_list =[('a1','b1','c1'), ('a1','b1','c2'), ('a2','b1','c1'), ('a2','b1','c2'), ]
        self.assertEqual(keys_data.get_key_list(),key_list)
        keys_data.set_headers('testitemb')
        key_list =[('a1','c1'), ('a1','c2'), ('a2','c1'), ('a2','c2'), ]
        self.assertEqual(keys_data.get_key_list(),key_list)


    def test_key_headers_mappings(self):
        """Testing the AssessData meta model's interaction with Keys()."""

        # Single column table (column_field = an index field)
        keys_data = Keys(TestMappings)
        keys_data.set_headers('testitemc')
        self.assertEqual(keys_data.column_field,'testitemc')
        self.assertEqual(keys_data.table_one_column,True)
        self.assertEqual(keys_data.index_headers,['testitema','testitemb'])
        self.assertEqual(keys_data.value_headers,['testitemc'])

        # Multi-column table (column_field = value_field)
        keys_data = Keys(TestMappings)
        keys_data.set_headers('testitemb')
        self.assertEqual(keys_data.column_field,'testitemb')
        self.assertEqual(keys_data.table_one_column,False)
        self.assertEqual(keys_data.index_headers,['testitema'])
        self.assertEqual(keys_data.value_headers,['b1'])

        # Multi-column table, alt column (column_field = value_field)
        keys_data = Keys(TestMappings)
        keys_data.set_headers('testitema')
        self.assertEqual(keys_data.column_field,'testitema')
        self.assertEqual(keys_data.table_one_column,False)
        self.assertEqual(keys_data.index_headers,['testitemb'])
        self.assertEqual(keys_data.value_headers,['a1','a2'])


    def test_key_get_key_list_mappings(self):
        """Testing key combos for Keys() row keys, data_model."""
        
        keys_data = Keys(TestMappings)
        keys_data.set_headers('testitemc')
        key_list =[('a1','b1'), ('a2','b1') ]
        self.assertEqual(keys_data.get_key_list(),key_list)
        keys_data.set_headers('testitemb')
        key_list =[('a1',), ('a2',) ]
        self.assertEqual(keys_data.get_key_list(),key_list)



        