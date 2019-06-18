from decimal import Decimal
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.table import AssessTable


rows_a = [   {'testitemc': 'c1', 'testitemb': 'b1', 'a1': Decimal('1.000'), 'a2': Decimal('5.000')},
             {'testitemc': 'c2', 'testitemb': 'b1', 'a1': Decimal('2.000'), 'a2': Decimal('6.000')}, ]   

rows_b = [   {'testitema': 'a1', 'testitemc': 'c1', 'b1': Decimal('1.000'), },
             {'testitema': 'a1', 'testitemc': 'c2', 'b1': Decimal('2.000'), },
             {'testitema': 'a2', 'testitemc': 'c1', 'b1': Decimal('5.000'), },
             {'testitema': 'a2', 'testitemc': 'c2', 'b1': Decimal('6.000'), }, ]

rows_c = [   {'testitema': 'a1', 'testitemb': 'b1', 'c1': Decimal('1.000'), 'c2': Decimal('2.000')},
             {'testitema': 'a2', 'testitemb': 'b1', 'c1': Decimal('5.000'), 'c2': Decimal('6.000')}, ]   

rows_v = [   {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': Decimal('1.000'), },
             {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c2', 'value': Decimal('2.000'), },
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c1', 'value': Decimal('5.000'), },
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c2', 'value': Decimal('6.000'), }, ]

rows_r = [   {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': Decimal('1.000'), },
             {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c2', 'value': Decimal('2.000'), },
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c1', 'value': Decimal('3.000'), },
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'value': Decimal('4.000'), },
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c1', 'value': Decimal('5.000'), },
             {'testitema': 'a2', 'testitemb': 'b1', 'testitemc': 'c2', 'value': Decimal('6.000'), }, 
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c1', 'value': Decimal('7.000'), },
             {'testitema': 'a1', 'testitemb': 'b2', 'testitemc': 'c2', 'value': Decimal('8.000'), },
             ]

class TableTestCase(TestCase):
    """Testing Table()."""
    
    def setUp(self):
        self.context = []
        v = Version()
        v.set_version_id("")
        self.version = v 
        v.save()

        TestItemA.objects.create(label='a1',version_first=v)
        TestItemA.objects.create(label='a2',version_first=v)
        TestItemB.objects.create(label='b1',version_first=v)
        TestItemB.objects.create(label='b2',version_first=v,version_last=v)
        TestItemC.objects.create(label='c1',version_first=v)
        TestItemC.objects.create(label='c2',version_first=v)

        a1 = TestItemA.objects.get(label='a1')
        a2 = TestItemA.objects.get(label='a2')
        b1 = TestItemB.objects.get(label='b1')
        b2 = TestItemB.objects.get(label='b2')
        c1 = TestItemC.objects.get(label='c1')
        c2 = TestItemC.objects.get(label='c2')

        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c1,value=1,version_first=v)
        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c2,value=2,version_first=v)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c1,value=3,version_first=v,version_last=v)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c2,value=4,version_first=v,version_last=v)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c1,value=5,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c2,value=6,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c1,value=7,version_first=v,version_last=v)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c2,value=8,version_first=v,version_last=v)


    def test_table_display_c(self):
        """Test multicolumn row c"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.set_rows('testitemc')
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
        self.assertEqual(context['header_list_items'],['b1'])
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
        self.assertEqual(context['row_list'],rows_v)


    def test_table_display_archived(self):
        """Test one-column archived value table"""
        t = AssessTable(TestData, str(self.version.id))
        t.load(False,[])
        t.set_rows('value')
        context = t.get_context()
        self.assertEqual(context['header_list_index'],['testitema','testitemb', 'testitemc'])
        self.assertEqual(context['header_list_items'],['value'])
        print(context['row_list'])
        
        self.assertEqual(context['row_list'],rows_r)
        