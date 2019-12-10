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


        # For this method, we do integration test using AssessTable.load() 
        # instead, since testing kwargs_filter will just be more or less a 
        # replica of the kwargs_filter_load method
        # These tests are performed in tests_table_data.py
        def test_kwargs_filter_load(self):
            pass