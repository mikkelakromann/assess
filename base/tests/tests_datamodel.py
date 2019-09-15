from decimal import Decimal
from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC, TestData

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


    def test_data_model_set_from_record(self):
        """Test multicolumn row c"""
        m = TestData()
        d = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '1' }
        m.set_fk_labels_objects()
        m.set_from_record_dict(d)
        self.assertEqual(m.value,Decimal(1))
        self.assertEqual(m.get_key(),tuple(['a1','b1','c1','value']))

    def test_data_model_set_from_cell(self):
        """Test multicolumn row c"""
        m = TestData()
        key = { 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1' }
        header = 'value'
        value = '1'
        column = 'value'
        m.set_fk_labels_objects()
        m.set_from_cell(key, header, value, column)
        self.assertEqual(m.value,Decimal(1))
        self.assertEqual(m.get_key(),tuple(['a1','b1','c1','value']))
