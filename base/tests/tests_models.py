from decimal import Decimal
from django.test import TestCase
from base.errors import NoFieldError, NoItemError
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData, TestMappings
from base.table import AssessTable
from base.messages import Messages

csv_str_2new = "a3\na4"
csv_str_1new1old = "a2\na3"
csv_str_2old = "a1\na2"


class TableModelTestCase(TestCase):
    """Testing AssessModel()."""
    
    def setUp(self):
        self.context = []
        self.v1 = Version()
        self.v1.set_version_id("")
        self.v1.save()
        self.v2 = Version()
        self.v2.set_version_id("")
        self.v2.save()

        TestItemA.objects.create(label='a1',version_first=self.v1)
        TestItemA.objects.create(label='a2',version_first=self.v1)
        TestItemB.objects.create(label='b1',version_first=self.v1)
        TestItemB.objects.create(label='b2',version_first=self.v1)
        TestItemC.objects.create(label='c1',version_first=self.v1)
        TestItemC.objects.create(label='c2',version_first=self.v1)

        self.a1 = TestItemA.objects.get(label='a1')
        self.a2 = TestItemA.objects.get(label='a2')
        self.b1 = TestItemB.objects.get(label='b1')
        self.b2 = TestItemB.objects.get(label='b2')
        self.c1 = TestItemC.objects.get(label='c1')
        self.c2 = TestItemC.objects.get(label='c2')
        
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=1,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c2,value=2,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=3,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=4)
        
        self.r1 = TestData.objects.get(value=1)
        self.r2 = TestData.objects.get(value=2)
        self.r3a = TestData.objects.get(value=3)
        self.r3b = TestData.objects.get(value=4)


    def test_commit(self):
        """Test that uncommitted rows are committed by setting version_last"""
        # Filters for current (fc) and proposed (fc)
        fc = {'version_first__isnull': False, 'version_last__isnull': True}
        fp = {'version_first__isnull': True, 'version_last__isnull': True }
        # Only the first two records are current
        current_records = list(TestData.objects.filter(**fc))
        self.assertEqual(current_records, [self.r1,self.r2,self.r3a])
        # Now commit the third record using AssessModel.commit()
        all_records = TestData.objects.filter(**fp)
        for record in all_records:
            record.commit(self.v2)
        current_records = list(TestData.objects.filter(**fc))
        self.assertEqual(current_records, [self.r1,self.r2,self.r3b])

    def test_set_from_cell_success(self):
        """Test that cell values can be set from single and multi-column"""
        t = TestData()
        t.set_fk_labels_objects()
        # Test the value table format
        key = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1' }
        header = 'value'
        value = '4'
        column_field = 'value'
        t.set_from_cell(key, header, value, column_field)
        self.assertEqual(t.value,Decimal('4'))
        # Test multicolumn with c as column
        key = { 'testitema': 'a1', 'testitemb': 'b1'}
        header = 'c1'
        value = '5'
        column_field = 'testitemc'
        t.set_from_cell(key, header, value, column_field)
        self.assertEqual(t.value,Decimal('5'))
        # Test multicolumn with b as column
        key = { 'testitema': 'a1', 'testitemc': 'c1'}
        header = 'b1'
        value = '6'
        column_field = 'testitemb'
        t.set_from_cell(key, header, value, column_field)
        self.assertEqual(t.value,Decimal('6'))

    def test_set_from_cell_failure(self):
        """Test that wrong headers and fields raises Exceptions"""
        t = TestData()
        t.set_fk_labels_objects()
        # Test the value table format
        key = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1' }
        value = '4'
        column_field = 'value'
        # bad header field should raise a NoFieldError for header
        header = 'bad_header_name'
        try:
            t.set_from_cell(key, header, value, column_field)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoFieldError('bad_header_name',TestData)))
        # bad value_field should raise a NoItemError for value_field
        column_field = 'bad_column_field'
        header = 'value'
        try:
            t.set_from_cell(key, header, value, column_field)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoFieldError('bad_column_field',TestData)))
        # Bad header in multi-column should raise NoItemError for header
        key = { 'testitema': 'a1', 'testitemb': 'b1' }
        value = '4'
        column_field = 'testitemc'
        header = 'bad_item_name'
        try:
            t.set_from_cell(key, header, value, column_field)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoItemError('bad_item_name',TestItemC)))

    def test_set_from_record_success(self):
        """Test that a record dict will update the model value."""
        t = TestData()
        t.set_fk_labels_objects()
        r = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '4' }
        t.set_from_record_dict(r)
        self.assertEqual(t.value, Decimal('4'))
        
    def test_set_from_record_failure(self):
        """Test that a record dict will update the model value."""
        t = TestData()
        t.set_fk_labels_objects()
        # Bad index name should raise NoFieldError
        r = { 'bad_index_name': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '4' }
        try:
            t.set_from_record_dict(r)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoFieldError('bad_index_name',TestData)))
        # Missing index fields in record dict should raise NoFieldError
        r = { 'testitema': 'a1', 'testitemb': 'b1', 'value': '4' }
        try:
            t.set_from_record_dict(r)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoFieldError('testitemc',TestData)))
        # Bad value name should raise NoITemError
        r = { 'testitema': 'bad_item', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '4' }
        try:
            t.set_from_record_dict(r)
        except NoItemError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoItemError('bad_item',TestItemA)))
        # Missing value_field should raise NoFieldError
        r = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1' }
        try:
            t.set_from_record_dict(r)
        except NoFieldError as e:
            e_msg = str(e)
        self.assertEqual(e_msg,str(NoFieldError('value',TestData)))
        
        
        