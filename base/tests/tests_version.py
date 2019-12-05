from django.test import TestCase
from .. version import Version
from .. models import TestItemA, TestItemB, TestItemC, TestData

class VersionTestCase(TestCase):
    """Show that defining methods with upper case ignores the test method."""
    
    def setUp(self):

        # First version for TestData
        self.v1 = Version(model_name='TestData')
        self.v1.set_version_id("")
        self.v1.save()
        # Archived for TestData
        self.v2 = Version(model_name='TestData')
        self.v2.set_version_id("")
        self.v2.save()
        # Unrelated to TestData
        self.v3 = Version(model_name='Not TestData')
        self.v3.set_version_id("")
        self.v3.save()
        # Proposed for TestData
        self.v4 = Version(model_name='TestData')
        self.v4.set_version_id("")
        self.v4.save()
        # Current, unrelated to TestData
        self.v5 = Version(model_name='Not TestData')
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

    def test_set_metrics(self):

        # First test a current version for v1 version
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=1,version_first=self.v1)
        proposed_values = [1]
        self.v1.set_metrics(TestData, proposed_values)
        self.assertEqual(self.v1.size,4)
        self.assertEqual(self.v1.dimension,'{2 x 2 x 1}')
        self.assertEqual(self.v1.cells,1)
        self.assertEqual(self.v1.metric,1)
#        self.assertEqual(self.v1.changes,1)

        # Change one record (by adding a new with same index items), and add 
        # an index item more to change dimensions
        TestData.objects.filter(pk=1).update(version_last=self.v2)
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=2,version_first=self.v2)
        TestItemC.objects.create(label='c2',version_first=self.v1)
        self.c2 = TestItemC.objects.get(label='c2')
        proposed_values = []
        self.v2.set_metrics(TestData, proposed_values)
        self.assertEqual(self.v2.size,8)
        self.assertEqual(self.v2.dimension,'{2 x 2 x 2}')
        self.assertEqual(self.v2.cells,1)
 #       self.assertEqual(self.v2.metric,2)
 #       self.assertEqual(self.v2.changes,1)

        # add anoter unique record within same version
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c2,value=4,version_first=self.v2)
        proposed_values = []
        self.v2.set_metrics(TestData, proposed_values)
        self.assertEqual(self.v2.size,8)
        self.assertEqual(self.v2.dimension,'{2 x 2 x 2}')
        self.assertEqual(self.v2.cells,2)
 #       self.assertEqual(self.v2.metric,3)
 #       self.assertEqual(self.v2.changes,2)
        
        # add a proposed record 
        TestData.objects.create(testitema=self.a2,testitemb=self.b1,testitemc=self.c2,value=6)
        v = Version(model_name='TestData')
        v.set_version_id('proposed')
        proposed_values = []
        v.set_metrics(TestData, proposed_values)
        self.assertEqual(v.size,8)
        self.assertEqual(v.dimension,'{2 x 2 x 2}')
        # Metric and cells are calculated for proposed records only
#        self.assertEqual(v.cells,1)
#        self.assertEqual(v.metric,6)
#        self.assertEqual(v.changes,1)
        
        # For this method, we do integration test using AssessTable.load() 
        # instead, since testing kwargs_filter will just be more or less a 
        # replica of the kwargs_filter_load method
        # These tests are performed in tests_table_data.py
        def test_kwargs_filter_load(self):
            pass