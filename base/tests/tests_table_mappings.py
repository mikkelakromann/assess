from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestMappings
from base.table import AssessTable

# Current version                       Archived version
#  a column         b column            a column        b column
#       a1  a2          b1  b2               a1  a2          b1  b2
#  b1   c1  c3      a1  c1  c2          b1   c2  c4      a1  c2  c2
#  b2   c2  c4      a2  c3  c4          b2   c2  c4      a2  c4  c4

rows_a = [   {'testitemb': 'b1', 'a1': 'c1', 'a1_id': 3, 'a1_key': "('a1', 'b1', 'testitemc')", 'a2': 'c3', 'a2_id': 5, 'a2_key': "('a2', 'b1', 'testitemc')"},
             {'testitemb': 'b2', 'a1': 'c2', 'a1_id': 4, 'a1_key': "('a1', 'b2', 'testitemc')", 'a2': 'c4', 'a2_id': 6, 'a2_key': "('a2', 'b2', 'testitemc')"},]   

rows_b = [   {'testitema': 'a1', 'b1': 'c1', 'b1_id': 3, 'b1_key': "('a1', 'b1', 'testitemc')", 'b2': 'c2', 'b2_id': 4, 'b2_key': "('a1', 'b2', 'testitemc')", },
             {'testitema': 'a2', 'b1': 'c3', 'b1_id': 5, 'b1_key': "('a2', 'b1', 'testitemc')", 'b2': 'c4', 'b2_id': 6, 'b2_key': "('a2', 'b2', 'testitemc')", }, ]


rows_nc = [  {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'testitemc_id': 3, 'testitemc_key': "('a1', 'b1', 'testitemc')" }, 
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'testitemc_id': 4, 'testitemc_key': "('a1', 'b2', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c3', 'testitemc_id': 5, 'testitemc_key': "('a2', 'b1', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c4', 'testitemc_id': 6, 'testitemc_key': "('a2', 'b2', 'testitemc')" }, ]

rows_v2 = [  {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'testitemc_id': 3, 'testitemc_key': "('a1', 'b1', 'testitemc')" }, 
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'testitemc_id': 4, 'testitemc_key': "('a1', 'b2', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c3', 'testitemc_id': 5, 'testitemc_key': "('a2', 'b1', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c4', 'testitemc_id': 6, 'testitemc_key': "('a2', 'b2', 'testitemc')" }, ]

rows_v1 = [  {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c2', 'testitemc_id': 1, 'testitemc_key': "('a1', 'b1', 'testitemc')" }, 
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'testitemc_id': 4, 'testitemc_key': "('a1', 'b2', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c4', 'testitemc_id': 2, 'testitemc_key': "('a2', 'b1', 'testitemc')" }, 
             {'testitema': 'a2', 'testitemb': 'b2', 'testitemc': 'c4', 'testitemc_id': 6, 'testitemc_key': "('a2', 'b2', 'testitemc')" }, ]


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
        TestItemC.objects.create(label='c3',version_first=v1)
        TestItemC.objects.create(label='c4',version_first=v1)

        a1 = TestItemA.objects.get(label='a1')
        a2 = TestItemA.objects.get(label='a2')
        b1 = TestItemB.objects.get(label='b1')
        b2 = TestItemB.objects.get(label='b2')
        c1 = TestItemC.objects.get(label='c1')
        c2 = TestItemC.objects.get(label='c2')
        c3 = TestItemC.objects.get(label='c3')
        c4 = TestItemC.objects.get(label='c4')

# Current version                       Archived version
#  a column         b column            a column        b column
#       a1  a2          b1  b2               a1  a2          b1  b2
#  b1   c1  c3      a1  c1  c2          b1   c2  c4      a1  c2  c2
#  b2   c2  c4      a2  c3  c4          b2   c2  c4      a2  c4  c4
 
        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c2,version_first=v1,version_last=v2)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c4,version_first=v1,version_last=v2)
        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c1,version_first=v2)
        TestMappings.objects.create(testitema=a1,testitemb=b2,testitemc=c2,version_first=v1)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c3,version_first=v2)
        TestMappings.objects.create(testitema=a2,testitemb=b2,testitemc=c4,version_first=v1)


    def test_table_display_b(self):
        """Test multicolumn with b as column"""
        t = AssessTable(TestMappings, "")
        t.load(False,[])
        t.set_rows('testitemb')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema'])
        self.assertEqual(context['header_list_items'],['b1','b2'])
        self.assertEqual(context['row_list'],rows_b)


    def test_table_display_a(self):
        """Test multicolumn with a as column"""
        t = AssessTable(TestMappings, "")
        t.load(False,[])
        t.set_rows('testitema')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitemb'])
        self.assertEqual(context['header_list_items'],['a1','a2'])
        self.assertEqual(context['row_list'],rows_a)


    def test_table_display_no_col(self):
        """Test multicolumn with no column"""
        t = AssessTable(TestMappings, "")
        t.load(False,[])
        t.set_rows('testitemc')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb'])
        self.assertEqual(context['header_list_items'],['testitemc'])
        self.assertEqual(context['row_list'],rows_nc)


    def test_table_display_archived1(self):
        """Test one-column archived value table"""
        t = AssessTable(TestMappings, '1')
        vKwargs = { 'version_first__lte': 1 }
        self.assertEqual(t.version.version_id,1)
        self.assertEqual(t.version.kwargs_filter_load(False),vKwargs)    
        t.load(False,[])
        t.set_rows('testitemc')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb'])
        self.assertEqual(context['header_list_items'],['testitemc'])        
        self.assertEqual(context['row_list'],rows_v1)


    def test_table_display_archived2(self):
        """Test one-column archived value table"""
        t = AssessTable(TestMappings, '2')
        vKwargs = { 'version_first__lte': 2 }
        self.assertEqual(t.version.version_id,2)
        self.assertEqual(t.version.kwargs_filter_load(False),vKwargs)    
        t.load(False,[])
        t.set_rows('testitemc')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb'])
        self.assertEqual(context['header_list_items'],['testitemc'])        
        self.assertEqual(context['row_list'],rows_v2)

# TODO: Create tests for POST and CSV save

