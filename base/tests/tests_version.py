from django.test import TestCase
from .. version import Version
from .. models import TestItemA, TestItemB, TestItemC, TestData

class VersionTestCase(TestCase):
    """Show that defining methods with upper case ignores the test method."""
    
    def setUp(self):

        # First version for TestData
        self.v1 = Version(model_name='TestData')
        self.v1.set_version_id("")
        self.v1.date = '2019-12-01'
        self.v1.save()
        # Archived for TestData
        self.v2 = Version(model_name='TestData')
        self.v2.set_version_id("")
        self.v1.date = '2019-12-02'
        self.v2.save()
        # Unrelated to TestData
        self.v3 = Version(model_name='Not TestData')
        self.v1.date = '2019-12-03'
        self.v3.set_version_id("")
        self.v3.save()
        # Proposed for TestData
        self.v4 = Version(model_name='TestData')
        self.v1.date = '2019-12-04'
        self.v4.set_version_id("")
        self.v4.save()
        # Current, unrelated to TestData
        self.v5 = Version(model_name='Not TestData')
        self.v1.date = '2019-12-05'
        self.v5.set_version_id("")
        self.v5.save()

        TestItemA.objects.create(label='a1',version_first=self.v1)
        TestItemA.objects.create(label='a2',version_first=self.v1)
        TestItemB.objects.create(label='b1',version_first=self.v1)
        TestItemB.objects.create(label='b2',version_first=self.v1)
        TestItemC.objects.create(label='c1',version_first=self.v1)

        self.a1 = TestItemA.objects.get(label='a1')
        self.a2 = TestItemA.objects.get(label='a2')
        self.b1 = TestItemB.objects.get(label='b1')
        self.b2 = TestItemB.objects.get(label='b2')
        self.c1 = TestItemC.objects.get(label='c1')

        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=1, version_first=self.v1, version_last=self.v2)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=12, version_first=self.v2, version_last=self.v4)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=14, version_first=self.v4)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=16)

    def test_str(self):
        v = Version(model_name='TestData', label='testing label')
        self.assertEqual(str(v),'testing label')
        
    def test_set_version_id(self):
        """Testing version initialised with str: 'current'"""

        v = Version(model_name='TestData')
        
        # Test current version
        v.set_version_id('current')
        self.assertEqual(v.version_id,4)
        self.assertEqual(v.status,"current")
        
        # Test current version (blank string), result should be current version
        # for TestData, as v has TestData as model
        v.set_version_id('')
        self.assertEqual(v.version_id,4)
        self.assertEqual(v.status,"current")

        # Test current version (string current version int)
        v.set_version_id('2')
        self.assertEqual(v.version_id,2)
        # TODO: Versions are proposed, current or specific
        # (while records are proposed, current or archived)
        self.assertEqual(v.status,"archived")
    
        # Test current version (blank string), result should be current version
        # for all nodels, as v2 no model
        v2 = Version()
        v2.set_version_id('')
        self.assertEqual(v2.version_id,5)
        self.assertEqual(v2.status,"current")

    def test_kwargs_filter_load(self):
        """Test the version kwargs filters."""
        v = Version(model_name='TestData')
        # Given a model name, 'current' should select latest version for table
        v.set_version_id('current')
        # Full table is filetred with non_null version_first and null ver_last
        # AssessTable() will take care of ignoring earlier records for same key
        act = v.kwargs_filter_load(False)
        exp = {'version_first__isnull': False, 'version_last__isnull': True}
        self.assertEqual(act,exp)
        # Changes are filtered with exact id for version_first
        act = v.kwargs_filter_load(True)
        exp = { 'version_first': 4 }
        self.assertEqual(act,exp)

        v.set_version_id('invalid_version_status_string')
        # Full table is filetred with non_null version_first and null ver_last
        # AssessTable() will take care of ignoring earlier records for same key
        act = v.kwargs_filter_load(False)
        exp = {'version_first__isnull': False, 'version_last__isnull': True}
        self.assertEqual(act,exp)
        # Changes are filtered with exact id for version_first
        act = v.kwargs_filter_load(True)
        exp = { 'version_first': 4 }
        self.assertEqual(act,exp)

        # Given an id, the version status is archived
        v.set_version_id('2')
        # The full table is everything with that id or lower
        act = v.kwargs_filter_load(False)
        exp = { 'version_first__lte': 2 }
        self.assertEqual(act,exp)
        # Changes onlu is everything with that exact id 
        act = v.kwargs_filter_load(True)
        exp = { 'version_first': 2 }
        self.assertEqual(act,exp)

        # Called with 'proposed', the version status is proposed
        v.set_version_id('proposed')
        # The full table is everything 
        act = v.kwargs_filter_load(False)
        exp = { 'version_last__isnull': True }
        self.assertEqual(act,exp)
        # Changes only is everything with no version_first
        act = v.kwargs_filter_load(True)
        exp = { 'version_first__isnull': True, 'version_last__isnull': True }
        self.assertEqual(act,exp)

    def test_kwargs_filter_misc(self):
        """Test the version kwargs filters, misc methods."""
        v = Version(model_name='TestData')
        v.set_version_id('1')
        # Archived
        act = v.kwargs_filter_archived()
        exp = { 'version_first__lte': 1 }
        self.assertEqual(act,exp)
        # Current
        act = v.kwargs_filter_current()
        exp = { 'version_first__isnull': False, 'version_last__isnull': True }
        self.assertEqual(act,exp)
        # Proposed
        act = v.kwargs_filter_proposed()
        exp = { 'version_first__isnull': True, 'version_last__isnull': True }
        self.assertEqual(act,exp)


            