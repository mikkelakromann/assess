from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData
from base.table import AssessTable


rows_a = [   {'testitemb': 'b1', 'testitemc': 'c1', 'a1': '1.000', 'a1_id': 1, 'a1_key': "('a1', 'b1', 'c1', 'value')", 'a2': '5.000', 'a2_id': 7,  'a2_key': "('a2', 'b1', 'c1', 'value')"},
             {'testitemb': 'b1', 'testitemc': 'c2', 'a1': '2.000', 'a1_id': 2, 'a1_key': "('a1', 'b1', 'c2', 'value')", 'a2': '6.000', 'a2_id': 8,  'a2_key': "('a2', 'b1', 'c2', 'value')"},
             {'testitemb': 'b2', 'testitemc': 'c1', 'a1': '3.000', 'a1_id': 5, 'a1_key': "('a1', 'b2', 'c1', 'value')", 'a2': '7.000', 'a2_id': 11, 'a2_key': "('a2', 'b2', 'c1', 'value')"},
             {'testitemb': 'b2', 'testitemc': 'c2', 'a1': '4.000', 'a1_id': 6, 'a1_key': "('a1', 'b2', 'c2', 'value')", 'a2': '8.000', 'a2_id': 12, 'a2_key': "('a2', 'b2', 'c2', 'value')"},]   

rows_b = [   {'testitema': 'a1', 'testitemc': 'c1', 'b1': '1.000', 'b1_id': 1, 'b1_key': "('a1', 'b1', 'c1', 'value')", 'b2': '3.000', 'b2_id': 5, 'b2_key': "('a1', 'b2', 'c1', 'value')", },
             {'testitema': 'a1', 'testitemc': 'c2', 'b1': '2.000', 'b1_id': 2, 'b1_key': "('a1', 'b1', 'c2', 'value')", 'b2': '4.000', 'b2_id': 6, 'b2_key': "('a1', 'b2', 'c2', 'value')", },
             {'testitema': 'a2', 'testitemc': 'c1', 'b1': '5.000', 'b1_id': 7, 'b1_key': "('a2', 'b1', 'c1', 'value')", 'b2': '7.000', 'b2_id': 11,'b2_key': "('a2', 'b2', 'c1', 'value')", },
             {'testitema': 'a2', 'testitemc': 'c2', 'b1': '6.000', 'b1_id': 8, 'b1_key': "('a2', 'b1', 'c2', 'value')", 'b2': '8.000', 'b2_id': 12,'b2_key': "('a2', 'b2', 'c2', 'value')", }, ]

rows_c = [   {'testitema': 'a1', 'testitemb': 'b1', 'c1': '1.000', 'c1_id': 1, 'c1_key': "('a1', 'b1', 'c1', 'value')", 'c2': '2.000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b2', 'c1': '3.000', 'c1_id': 5, 'c1_key': "('a1', 'b2', 'c1', 'value')", 'c2': '4.000', 'c2_id': 6, 'c2_key': "('a1', 'b2', 'c2', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b1', 'c1': '5.000', 'c1_id': 7, 'c1_key': "('a2', 'b1', 'c1', 'value')", 'c2': '6.000', 'c2_id': 8, 'c2_key': "('a2', 'b1', 'c2', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b2', 'c1': '7.000', 'c1_id': 11,'c1_key': "('a2', 'b2', 'c1', 'value')", 'c2': '8.000', 'c2_id': 12,'c2_key': "('a2', 'b2', 'c2', 'value')"}, ]   

rows_v2 = [  {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '1.000', 'value_id': 1, 'value_key': "('a1', 'b1', 'c1', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c2', 'value': '2.000', 'value_id': 2, 'value_key': "('a1', 'b1', 'c2', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c1', 'value': '3.000', 'value_id': 5, 'value_key': "('a1', 'b2', 'c1', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'value': '4.000', 'value_id': 6, 'value_key': "('a1', 'b2', 'c2', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '5.000', 'value_id': 7, 'value_key': "('a2', 'b1', 'c1', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c2', 'value': '6.000', 'value_id': 8, 'value_key': "('a2', 'b1', 'c2', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c1', 'value': '7.000', 'value_id': 11,'value_key': "('a2', 'b2', 'c1', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c2', 'value': '8.000', 'value_id': 12,'value_key': "('a2', 'b2', 'c2', 'value')"}, ]

rows_v1 = [  {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '1.000', 'value_id': 1, 'value_key': "('a1', 'b1', 'c1', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c2', 'value': '2.000', 'value_id': 2, 'value_key': "('a1', 'b1', 'c2', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c1', 'value': '13.000','value_id': 3, 'value_key': "('a1', 'b2', 'c1', 'value')"},
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'value': '14.000','value_id': 4, 'value_key': "('a1', 'b2', 'c2', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '5.000', 'value_id': 7, 'value_key': "('a2', 'b1', 'c1', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c2', 'value': '6.000', 'value_id': 8, 'value_key': "('a2', 'b1', 'c2', 'value')"}, 
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c1', 'value': '17.000','value_id': 9, 'value_key': "('a2', 'b2', 'c1', 'value')"},
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c2', 'value': '18.000','value_id': 10,'value_key': "('a2', 'b2', 'c2', 'value')"}, ]


class TableDataTestCase(TestCase):
    """Testing Table()."""
    
    def setUp(self):
        self.context = []
        v1 = Version()
        v1.set_version_id("")
        v1.save()
        v2 = Version()
        v2.set_version_id("")
        v2.save()

        TestItemA.objects.create(label='a1',version_first=v1)
        TestItemA.objects.create(label='a2',version_first=v1)
        TestItemB.objects.create(label='b1',version_first=v1)
        TestItemB.objects.create(label='b2',version_first=v1)
        TestItemC.objects.create(label='c1',version_first=v1)
        TestItemC.objects.create(label='c2',version_first=v1)

        a1 = TestItemA.objects.get(label='a1')
        a2 = TestItemA.objects.get(label='a2')
        b1 = TestItemB.objects.get(label='b1')
        b2 = TestItemB.objects.get(label='b2')
        c1 = TestItemC.objects.get(label='c1')
        c2 = TestItemC.objects.get(label='c2')

        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c1,value=1,version_first=v1)
        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c2,value=2,version_first=v1)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c1,value=13,version_first=v1,version_last=v2)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c2,value=14,version_first=v1,version_last=v2)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c1,value=3,version_first=v2)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c2,value=4,version_first=v2)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c1,value=5,version_first=v1)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c2,value=6,version_first=v1)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c1,value=17,version_first=v1,version_last=v2)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c2,value=18,version_first=v1,version_last=v2)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c1,value=7,version_first=v2)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c2,value=8,version_first=v2)


    def test_table_display_c(self):
        """Test multicolumn row c"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.set_rows('testitemc')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema', 'testitemb'])
        self.assertEqual(context['header_list_items'],['c1', 'c2'])
        self.assertEqual(context['row_list'],rows_c)


    def test_table_display_c_bad_field(self):
        """Test multicolumn row c, table must default to model.column_field"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        # PRoviding a bad field name make table use default model.column_field
        t.set_rows('bad_field_name')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema', 'testitemb'])
        self.assertEqual(context['header_list_items'],['c1', 'c2'])
        self.assertEqual(context['row_list'],rows_c)


    def test_table_display_b(self):
        """Test multicolumn row b"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.set_rows('testitemb')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema', 'testitemc'])
        self.assertEqual(context['header_list_items'],['b1','b2'])
        self.assertEqual(context['row_list'],rows_b)


    def test_table_display_a(self):
        """Test multicolumn row a"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.set_rows('testitema')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitemb', 'testitemc'])
        self.assertEqual(context['header_list_items'],['a1','a2'])
        self.assertEqual(context['row_list'],rows_a)


    def test_table_display_val(self):
        """Test one-column value table"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.set_rows('value')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb', 'testitemc'])
        self.assertEqual(context['header_list_items'],['value'])
        self.assertEqual(context['row_list'],rows_v2)


    def test_table_display_archived1(self):
        """Test one-column archived value table"""
        t = AssessTable(TestData, '1')
        vKwargs = { 'version_first__lte': 1 }
        self.assertEqual(t.version.version_id,1)
        self.assertEqual(t.version.kwargs_filter_load(False),vKwargs)    
        t.load(False,[])
        t.set_rows('value')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb', 'testitemc'])
        self.assertEqual(context['header_list_items'],['value'])        
        self.assertEqual(context['row_list'],rows_v1)


    def test_table_display_archived2(self):
        """Test one-column archived value table"""
        t = AssessTable(TestData, '2')
        vKwargs = { 'version_first__lte': 2 }
        self.assertEqual(t.version.version_id,2)
        self.assertEqual(t.version.kwargs_filter_load(False),vKwargs)    
        t.load(False,[])
        t.set_rows('value')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb', 'testitemc'])
        self.assertEqual(context['header_list_items'],['value'])        
        self.assertEqual(context['row_list'],rows_v2)
                