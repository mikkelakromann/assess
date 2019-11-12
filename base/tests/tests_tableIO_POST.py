import traceback
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.tableIO import AssessTableIO
from base.errors import KeyNotFound, KeyInvalid, NoFieldError

delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }


POST_1_7 = { "('a1','b1','c1','value')": '1.000', "('a1','b1','c2','value')": '2.000', 
             "('a1','b2','c1','value')": '3.000', "('a1','b2','c2','value')": '4.000', 
             "('a2','b1','c1','value')": '5.000', "('a2','b1','c2','value')": '6.000', 
             "('a2','b2','c1','value')": '7.000',  }
values_data_1_7 = ['1,000','2,000','3,000','4,000','5,000','6,000','7,000']


POST_1_8 = { "('a1','b1','c1','value')": '1.000', "('a1','b1','c2','value')": '2.000', 
             "('a1','b2','c1','value')": '3.000', "('a1','b2','c2','value')": '4.000', 
             "('a2','b1','c1','value')": '5.000', "('a2','b1','c2','value')": '6.000', 
             "('a2','b2','c1','value')": '7.000', "('a2','b2','c2','value')": '8.000', 
             }
values_data_1_8 = ['1,000','2,000','3,000','4,000','5,000','6,000','7,000','8,000']

POST_1_9 = { "('a1','b1','c1','value')": '1.000', "('a1','b1','c2','value')": '2.000', 
             "('a1','b2','c1','value')": '3.000', "('a1','b2','c2','value')": '4.000', 
             "('a2','b1','c1','value')": '5.000', "('a2','b1','c2','value')": '6.000', 
             "('a2','b2','c1','value')": '7.000', "('a2','b2','c2','value')": '118.000', 
             "('a2','b2','c2','value')": '18.000', }
values_data_1_9 = ['1,000','2,000','3,000','4,000','5,000','6,000','7,000','18,000']

POST_invalid_length = { "('a1','b1','c1')": '1' }
POST_invalid_label = { "('a1','b1','bad_item','value')": '1' }
POST_invalid_value_field = { "('a1','b1','c1','bad_field')": '1' }

mappings_POST_1_3 = { 
    "('a1','b1','testitemc')": 'c1', "('a1','b2','testitemc')": 'c2', 
    "('a2','b1','testitemc')": 'c1',  
}
values_mappings_1_3 = ['c1','c2','c1']

mappings_POST_1_4 = { 
    "('a1','b1','testitemc')": 'c1', "('a1','b2','testitemc')": 'c2', 
    "('a2','b1','testitemc')": 'c1', "('a2','b2','testitemc')": 'c2',  
}
values_mappings_1_4 = ['c1','c2','c1','c2']

mappings_POST_1_5 = { 
    "('a1','b1','testitemc')": 'c1', "('a1','b2','testitemc')": 'c2', 
    "('a2','b1','testitemc')": 'c1', "('a2','b2','testitemc')": 'c2',  
    "('a2','b2','testitemc')": 'c1', }
values_mappings_1_5 = ['c1','c2','c1','c1']


def print_traceback(errors):
    """Print list of AssessErrors in traceback form."""
    for error in errors:
        print(error)
        print("".join(traceback.format_tb(error.__traceback__)))
 

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

#        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c1,value=1,version_first=v)
#        TestData.objects.create(testitema=a1,testitemb=b1,testitemc=c2,value=2,version_first=v)
#        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c1,value=3,version_first=v)
#        TestData.objects.create(testitema=a1,testitemb=b2,testitemc=c2,value=4,version_first=v)
#        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c1,value=5,version_first=v)
#        TestData.objects.create(testitema=a2,testitemb=b1,testitemc=c2,value=6,version_first=v)
#        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c1,value=7,version_first=v)
#        TestData.objects.create(testitema=a2,testitemb=b2,testitemc=c2,value=8,version_first=v)


    def test_parse_post_data(self):
        """Test parsing of POST key/value pairs for data_model in TableIO """
        
        # Test fully loaded table (8 values) in POST
        tIO = AssessTableIO(TestData,delimiters)
        records = tIO.parse_POST(POST_1_8)
        values = []
        for record in records.values():
            values.append(record.get_value())
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_1_8)

        # Test partly loaded table (7 values) in POST
        tIO = AssessTableIO(TestData,delimiters)
        records = tIO.parse_POST(POST_1_7)
        values = []
        for record in records.values():
            values.append(record.get_value())
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_1_7)

        # Test overloaded table (9 values) in POST
        tIO = AssessTableIO(TestData,delimiters)
        records = tIO.parse_POST(POST_1_9)
        values = []
        for record in records.values():
            values.append(record.get_value())
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_data_1_9)

    def test_parse_post_data_invalid(self):
        # Test that an invalid key length in POST results in an error and that
        # the POST entry is not added to the records
        tIO = AssessTableIO(TestData,delimiters)
        records = tIO.parse_POST(POST_invalid_length)
        key = list(POST_invalid_length.keys()).pop()
        self.assertEqual(str(tIO.errors.pop()),str(KeyInvalid(key, TestData)))
        self.assertEqual(records,{})
        # Test that an invalid key length in POST results in an error and that
        # the POST entry is not added to the records
        records = tIO.parse_POST(POST_invalid_label)
        key = 'bad_item in ' + list(POST_invalid_label.keys()).pop()
        self.assertEqual(str(tIO.errors.pop()),str(KeyNotFound(key, TestData)))
        self.assertEqual(records,{})
        # Test that an invalid value field name in POST results in an error 
        # and that the POST entry is not added to the records
        records = tIO.parse_POST(POST_invalid_value_field)
        error_msg = str(NoFieldError('bad_field', TestData))
        self.assertNotEqual(len(tIO.errors),0)
        if len(tIO.errors) > 0:
            self.assertEqual(str(tIO.errors.pop()),error_msg)
        self.assertEqual(records,{})
        

    def test_parse_post_mapppings(self):
        """Test parsing of POST key/value pairs for data_model in TableIO """
        
        # Test partly loaded table (3 values) in POST
        tIO = AssessTableIO(TestMappings,delimiters)
        records = tIO.parse_POST(mappings_POST_1_3)
        values = []
        for record in records.values():
            values.append(str(record.get_value()))
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_1_3)

        # Test fully loaded table (4 values) in POST
        tIO = AssessTableIO(TestMappings,delimiters)
        records = tIO.parse_POST(mappings_POST_1_4)
        values = []
        for record in records.values():
            values.append(str(record.get_value()))
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_1_4)

        # Test overloaded table (5 values) in POST
        tIO = AssessTableIO(TestMappings,delimiters)
        records = tIO.parse_POST(mappings_POST_1_5)
        values = []
        for record in records.values():
            values.append(str(record.get_value()))
        print_traceback(tIO.errors)
        self.assertEqual(tIO.errors,[])
        self.assertEqual(values,values_mappings_1_5)
