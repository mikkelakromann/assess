from django.test import TestCase

from .. errors import NoFieldError, NoItemError
from .. history import History
from .. models import Version,TestItemA, TestItemB, TestItemC, TestData
from .. table import AssessTable
from .. messages import Messages

class TableModelTestCase(TestCase):
    """Testing AssessModel()."""
    
    def setUp(self):
        self.context = []
        self.v1 = Version(**{'model_name': 'testdata', 'date': 1})
        self.v1.set_version_id("")
        self.v1.save()
        self.v2 = Version(**{'model_name': 'testdata', 'date': 2})
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
        
        # First record is archived
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=1,version_first=self.v1,version_last=self.v2)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c2,value=2,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=3,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=4,version_first=self.v1)
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=4,version_first=self.v1)
        # First record is replaced by another in v2
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=10,version_first=self.v2)
        # Last record has a proposed update
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c1,value=14)


    def test_commit(self):
        """Test that uncommitted rows are committed by setting version_last"""
        history = History(TestData)
        a = {}
        actual = []
        for version in history.context_data:
            a['status'] = version.status
            a['version_id'] = version.id
            a['version_link'] = version.version_link
            a['idlink'] = version.idlink
            actual.append(a.copy())
        expected = [{'status': 'Proposed', 'version_id': None, 'version_link': 'testdata_version', 'idlink': 'proposed', },
                    {'status': 'Current',  'version_id': 2, 'version_link': 'testdata_version', 'idlink': 2 },
                    {'status': 'Archived', 'version_id': 1, 'version_link': 'testdata_version', 'idlink': 1, }, ]
        self.assertEqual(actual,expected)
