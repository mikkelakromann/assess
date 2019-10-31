import pandas 
from pandas.util.testing import assert_frame_equal
import traceback
from decimal import Decimal
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, \
                        TestMappings
from base.errors import NotDecimalError, NoItemError
from base.tableIO import AssessTableIO
from base.table import AssessTable 

delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }

def print_traceback(errors):
    """Print list of AssessErrors in traceback form."""
    for error in errors:
        print(error)
        print("".join(traceback.format_tb(error.__traceback__)))


eleA = ['a1','a1','a1','a1','a2','a2','a2','a2']
eleB = ['b1','b1','b2','b2','b1','b1','b2','b2']
eleC = ['c1','c2','c1','c2','c1','c2','c1','c2']
val = [Decimal(1),Decimal(2),Decimal(3),Decimal(4),Decimal(5),Decimal(6),Decimal(7),Decimal(8)]

dfd = pandas.DataFrame({'testitema': eleA, 'testitemb': eleB, 'testitemc': eleC, 'value': val})
dfm = pandas.DataFrame({'testitema': eleA, 'testitemb': eleB, 'testitemc': eleC})

class TableIOTestCase(TestCase):
    """Testing TableIO()."""
    
    def setUp(self):
        v = Version()
        v.save()
        self.v = v
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


        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c1,version_first=v)
        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c2,version_first=v)
        TestMappings.objects.create(testitema=a1,testitemb=b2,testitemc=c1,version_first=v)
        TestMappings.objects.create(testitema=a1,testitemb=b2,testitemc=c2,version_first=v)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c1,version_first=v)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c2,version_first=v)
        TestMappings.objects.create(testitema=a2,testitemb=b2,testitemc=c1,version_first=v)
        TestMappings.objects.create(testitema=a2,testitemb=b2,testitemc=c2,version_first=v)


    def test_parse_dataframe_data_success(self):
        """Test parsing of dataframe into data_model in TableIO """
        # TODO: look for ways that this function might fail and test
        # Test fully loaded table (8 values) in POST
        t = AssessTable(TestData,'1')
        t.load(False)
        tIO = AssessTableIO(TestData,delimiters)
        tIO.keys.set_headers('value')
        DF =  []
        # We must unpack key/value from record, as objects cannot expected to 
        # identical between dataframes and load (TODO: why not???)
        for key,record in tIO.parse_dataframe(dfd).items():
            DF.append({key: record.get_value()})
        DB = []
        for key,record in t.records.items():
            DB.append({key: record.get_value()})
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(DB,DF)

    def test_parse_dataframe_data_failure(self):
        """Test that method fail when index items and values are invalid"""
        tIO = AssessTableIO(TestData,delimiters)
        tIO.keys.set_headers('value')
        # Test invalid decimal number
        dfe = pandas.DataFrame({'testitema': ['a1'], 'testitemb': ['b1'], 'testitemc': ['c1'], 'value': 'XX'})        
        tIO.parse_dataframe(dfe)
        e1 = str(tIO.errors.pop())
        e2 = str(NotDecimalError('XX',TestData))
        self.assertEqual(e1,e2)
        # Test invalid index item
        dfe = pandas.DataFrame({'testitema': ['a1'], 'testitemb': ['b1'], 'testitemc': ['BADITEM'], 'value': '1'})        
        tIO.parse_dataframe(dfe)
        e1 = str(tIO.errors.pop())
        e2 = str(NoItemError('BADITEM',TestItemC))
        self.assertEqual(e1,e2)
        # Test invalid index item in mappings_model
        tIO = AssessTableIO(TestMappings,delimiters)
        tIO.keys.set_headers('testitemc')
        dfe = pandas.DataFrame({'testitema': ['a1'], 'testitemb': ['b1'], 'testitemc': ['BADITEM'] })        
        tIO.parse_dataframe(dfe)
        e1 = str(tIO.errors.pop())
        e2 = str(NoItemError('BADITEM',TestMappings))
        self.assertEqual(e1,e2)

    # Parse dataframe to records

    def test_get_dataframe_success(self):
        """Test that the database can be read and exported as dataframe."""
        # Test data_model 
        tIO = AssessTableIO(TestData,delimiters)
        tIO.keys.set_headers('value')
        db = tIO.get_dataframe(self.v)                
        assert_frame_equal(db,dfd)
        # Test that mappings_model
        tIO = AssessTableIO(TestMappings,delimiters)
        tIO.keys.set_headers('testitemc')
        db = tIO.get_dataframe(self.v)                
        assert_frame_equal(db,dfm)
        
    def test_get_dataframe_failure(self):
        """Test that the database can be read and exported as dataframe."""
        # Test that method returns empty dataframe on no database data
        TestData.objects.all().delete()
        tIO = AssessTableIO(TestData,delimiters)
        tIO.keys.set_headers('value')
        db = tIO.get_dataframe(self.v)                
        dfe = pandas.DataFrame()
        assert_frame_equal(db,dfe)

    
        