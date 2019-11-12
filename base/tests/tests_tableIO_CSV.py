from django.test import TestCase
from base.errors import AssessError, NoItemError, NoFieldError, CSVheaderMalformed, CSVwrongColumnCount, CSVfieldNotFound
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.tableIO import AssessTableIO

delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }

values_data_c = ['1,000','2,000','5,000','6,000']
csv_data_string_c = """testitema\ttestitemb\tc1\tc2
a1\tb1\t1\t2
a2\tb1\t5\t6"""

values_data_a = ['1,000','5,000','2,000','6,000']
csv_data_string_a = """testitemb\ttestitemc\ta1\ta2
b1\tc1\t1\t5
b1\tc2\t2\t6"""

values_data_b = ['1,000','2,000','5,000','6,000']
csv_data_string_b = """testitema\ttestitemc\tb1
a1\tc1\t1
a1\tc2\t2
a2\tc1\t5
a2\tc2\t6
"""

values_data_val = ['1,000','2,000','5,000','6,000']
csv_data_string_val = """testitema\ttestitemb\ttestitemc\tvalue
a1\tb1\tc1\t1
a1\tb1\tc2\t2
a2\tb1\tc1\t5
a2\tb1\tc2\t6
"""

# Add the archived b2 item to the table
# TableIO should return no records
values_data_bb = []
csv_data_string_bb = """testitema\ttestitemc\tb1\tb2
a1\tc1\t1\t3
a1\tc2\t2\t4
a2\tc1\t5\t7
a2\tc2\t6\t8
"""

values_mappings_a = ['c1','c2']
csv_mappings_string_a = """testitemb\ta1\ta2
b1\tc1\tc2
"""

values_mappings_b = ['c1','c2']
csv_mappings_string_b = """testitema\tb1
a1\tc1
a2\tc2
"""

values_mappings_c = ['c1','c2']
csv_mappings_string_c = """testitema\ttestitemb\ttestitemc
a1\tb1\tc1
a2\tb1\tc2
"""


class TableIOTestCase(TestCase):
    """Testing TableIO()."""
    
    def setUp(self):
        v = Version()
        v.save()
        TestItemA.objects.create(label='a1',version_first=v)
        TestItemA.objects.create(label='a2',version_first=v)
        TestItemB.objects.create(label='b1',version_first=v)
        TestItemB.objects.create(label='b2',version_first=v,version_last=v)
        TestItemC.objects.create(label='c1',version_first=v)
        TestItemC.objects.create(label='c2',version_first=v)
#        TestData.objects.create(testitema__id=1,testitemb__id=1,testitemc__id=1,value=1,version_first=v)
#        TestData.objects.create(testitema='a1',testitemb='b1',testitemc='c2',value=2,version_first=v)
#        TestData.objects.create(testitema='a1',testitemb='b2',testitemc='c1',value=3,version_first=v,version_last=v)
#        TestData.objects.create(testitema='a1',testitemb='b2',testitemc='c2',value=4,version_first=v,version_last=v)
#        TestData.objects.create(testitema='a2',testitemb='b1',testitemc='c1',value=5,version_first=v)
#        TestData.objects.create(testitema='a2',testitemb='b1',testitemc='c2',value=6,version_first=v)
#        TestData.objects.create(testitema='a2',testitemb='b2',testitemc='c1',value=7,version_first=v,version_last=v)
#        TestData.objects.create(testitema='a2',testitemb='b2',testitemc='c2',value=8,version_first=v,version_last=v)


    def test_parse_csv_data(self):
        """Test parsing of csv strings for data_model in TableIO """
        
        # Test multi-colunm input 
        POST = {'column_field': 'testitemc', 'csv_string': csv_data_string_c }
        tIO = AssessTableIO(TestData,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(record.get_value())
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_c)

        # Test multi-colunm input, alternative column 
        POST = {'column_field': 'testitema', 'csv_string': csv_data_string_a }
        tIO = AssessTableIO(TestData,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(record.get_value())
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_a)

        # Test multi-colunm input, another alternative column 
        POST = {'column_field': 'testitemb', 'csv_string': csv_data_string_b }
        tIO = AssessTableIO(TestData,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(record.get_value())
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_b)

        # Test multi-colunm input, another alternative, but with archived index 
        POST = {'column_field': 'testitemb', 'csv_string': csv_data_string_bb }
        tIO = AssessTableIO(TestData,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(record.get_value())
        # This input is supposed to raise an error and return empty
        self.assertNotEqual(tIO.errors,[])
        self.assertEqual(values,[])

        # Test one-colunm input
        POST = {'column_field': 'value', 'csv_string': csv_data_string_val }
        tIO = AssessTableIO(TestData,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,True)
        for record in records.values():
            values.append(record.get_value())
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_val)


    def test_parse_csv_mappings(self):
        """Test parsing of csv strings for mappings_model in TableIO """
        
        # Test multi-colunm input 
        POST = {'column_field': 'testitemb', 'csv_string': csv_mappings_string_b }
        tIO = AssessTableIO(TestMappings,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(str(record.get_value()))
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_b)

        # Test multi-colunm input, alternative 
        POST = {'column_field': 'testitema', 'csv_string': csv_mappings_string_a }
        tIO = AssessTableIO(TestMappings,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,False)
        for record in records.values():
            values.append(str(record.get_value()))
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_a)

        # Test one-colunm input
        POST = {'column_field': 'testitemc', 'csv_string': csv_mappings_string_c }
        tIO = AssessTableIO(TestMappings,delimiters)
        values = []
        records = tIO.parse_csv(POST)
        self.assertEqual(tIO.keys.table_one_column,True)
        for record in records.values():
            values.append(str(record.get_value()))
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_c)


    def test_parse_csv_data_failure(self):
        """Test parsing of csv strings for mappings_model in TableIO - failures."""
        e1 = AssessError()
        e2 = AssessError()
        
        # Test malformed header
        ch = ['testitemBAD','testitemb','c1','c2']
        ct = ['testitema','testitemb','c1','c2']
        csv_data_string_c_bad_header = """testitemBAD\ttestitemb\tc1\tc2
a1\tb1\t1\t2
a2\tb1\t5\t6"""
        POST = {'column_field': 'testitemc', 'csv_string': csv_data_string_c_bad_header}
        tIO = AssessTableIO(TestData,delimiters)
        tIO.parse_csv(POST)
        msg = str(NoFieldError('testitemBAD',TestData))
        e2 = CSVheaderMalformed(ch,ct,msg,TestData)
        e1 = tIO.errors.pop()
        self.assertEqual(str(e1),str(e2))
        # Test wrong line count: First dataline has 1 too many, last 1 too few
        csv_data_string_c_bad_count = """testitema\ttestitemb\tc1\tc2
a1\tb1\t1\t2\t99
a2\tb1\t5"""
        POST = {'column_field': 'testitemc', 'csv_string': csv_data_string_c_bad_count}
        ch = ['testitema','testitemb','c1','c2']
        tIO = AssessTableIO(TestData,delimiters)
        tIO.parse_csv(POST)
        # One too many row columns
        row = ['a2','b1','5']
        e2 = CSVwrongColumnCount(row,ch,'',TestData)
        e1 = tIO.errors.pop()
        self.maxDiff = None
        self.assertEqual(str(e1),str(e2))
        # Test wrong key
        row = ['a1','b1','1','2','99']
        e2 = CSVwrongColumnCount(row,ch,'',TestData)
        e1 = tIO.errors.pop()
        self.maxDiff = None
        self.assertEqual(str(e1),str(e2))
        # Test bad index item in data row
        csv_data_string_c_bad_count = """testitema\ttestitemb\tc1\tc2
a1\tb1\t1\t2
BADITEM\tb1\t5\t6"""
        POST = {'column_field': 'testitemc', 'csv_string': csv_data_string_c_bad_count}
        ch = ['testitema','testitemb','c1','c2']
        tIO = AssessTableIO(TestData,delimiters)
        tIO.parse_csv(POST)
        # One too many row columns
        row = ['BADITEM','b1','5','6']
        msg = str(NoItemError('BADITEM', TestItemA))
        e2 = CSVfieldNotFound(row, ch, msg, TestData)
        e1 = tIO.errors.pop()
        self.maxDiff = None
        self.assertEqual(str(e1),str(e2))
