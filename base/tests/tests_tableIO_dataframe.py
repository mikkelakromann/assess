import pandas 

import traceback
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.tableIO import AssessTableIO
from base.table import AssessTable 

delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }

def print_traceback(errors):
    """Print list of AssessErrors in traceback form."""
    for error in errors:
        print(error)
        print("".join(traceback.format_tb(error.__traceback__)))


eleA = ['a1','a1','a1','a1','a2','a2','a2','a2','a2']
eleB = ['b1','b1','b2','b2','b1','b1','b2','b2','b2']
eleC = ['c1','c2','c1','c2','c1','c2','c1','c2','c2']
val = [1,2,3,4,5,6,7,18,8]

df = pandas.DataFrame({'testitema': eleA, 'testitemb': eleB, 'testitemc': eleC, 'value': val})

class TableIOTestCase(TestCase):
    """Testing TableIO()."""
    
    def setUp(self):
        v = Version()
        v.save()
        TestItemA.objects.create(label='a1',version_first=v)
        TestItemA.objects.create(label='a2',version_first=v)
        TestItemB.objects.create(label='b1',version_first=v)
        TestItemB.objects.create(label='b2',version_first=v)
        TestItemC.objects.create(label='c1',version_first=v)
        TestItemC.objects.create(label='c2',version_first=v)
        a1 = TestItemA.objects.get(pk=1)
        a2 = TestItemA.objects.get(pk=2)
        b1 = TestItemB.objects.get(pk=1)
        b2 = TestItemB.objects.get(pk=2)
        c1 = TestItemC.objects.get(pk=1)
        c2 = TestItemC.objects.get(pk=2)

        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c1,value=1,version_first=v)
        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c2,value=2,version_first=v)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c1,value=3,version_first=v)
        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c2,value=4,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c1,value=5,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c2,value=6,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c1,value=7,version_first=v)
        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c2,value=8,version_first=v)


    def test_parse_dataframe_data(self):
        """Test parsing of POST key/value pairs for data_model in TableIO """
        
        # Test fully loaded table (8 values) in POST
        t = AssessTable(TestData,'1')
        t.load(False)
        tIO = AssessTableIO(TestData,delimiters)
        tIO.keys.set_headers('value')
        DF =  []
        # We must unpack key/value from record, as objects cannot expected to 
        # identical between dataframes and load (TODO: why not???)
        for key,record in tIO.parse_dataframe(df).items():
            DF.append({key: record.get_value()})
        DB = []
        for key,record in t.records.items():
            DB.append({key: record.get_value()})
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(DB,DF)
