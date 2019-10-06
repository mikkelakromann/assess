from decimal import Decimal
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestMappings
from base.errors import NoFieldError, NoItemError,NotDecimal

class DataModelTestCase(TestCase):
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

        self.a1 = a1
        self.a2 = a2
        self.b1 = b1
        self.b2 = b2
        self.c1 = c1
        self.c2 = c1
        self.c3 = c1
        self.c4 = c1

# Current version                       Archived version
#  a column         b column            a column        b column
#       a1  a2          b1  b2               a1  a2          b1  b2
#  b1   c1  c3      a1  c1  c2          b1   c2  c4      a1  c2  c2
#  b2   c2  c4      a2  c3  c4          b2   c2  c4      a2  c4  c4
 
        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c2,version_first=v1,version_last=v2)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c4,version_first=v1,version_last=v2)
        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c1,version_first=v1)
        TestMappings.objects.create(testitema=a1,testitemb=b2,testitemc=c2,version_first=v1)
        TestMappings.objects.create(testitema=a2,testitemb=b1,testitemc=c3,version_first=v2)
        TestMappings.objects.create(testitema=a2,testitemb=b2,testitemc=c4,version_first=v1)



    def test_data_model_set_from_record(self):
        """Test multicolumn row c"""
        m = TestMappings()
        m.set_fk_labels_objects()
        d = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1' }
        m.set_from_record_dict(d)
        self.assertEqual(m.get_key(),tuple(['a1','b1','testitemc']))
        self.assertEqual(m.get_value(),self.c1)
        

    def test_data_model_set_from_cell(self):
        """Test multicolumn row c"""
        m = TestMappings()
        key = { 'testitema': 'a1', 'testitemb': 'b1' }
        header = 'testitemc'
        value = 'c1'
        column = 'testitemc'
        m.set_fk_labels_objects()
        m.set_from_cell(key, header, value, column)
        self.assertEqual(m.get_key(),tuple(['a1','b1','testitemc']))
        self.assertEqual(m.get_value(),self.c1)

    def test_set_value_success(self):
        """Test that a record dict will update the model value."""
        m = TestMappings()
        m.set_fk_labels_objects()
        m.set_value('c1')
        self.assertEqual(m.get_value(),self.c1)

    def test_set_value_failure(self):
        m = TestMappings()
        m.set_fk_labels_objects()
        # Obviously wrong string
        label_str = 'cc1'
        try:
            m.set_value(label_str)
        except NoItemError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoItemError(label_str,TestMappings)))

