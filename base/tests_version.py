from django.test import TestCase
from base.version import Version

class VersionTestCase(TestCase):
    """Show that defining methods with upper case ignores the test method."""
    
    def setUp(self):
        
        Version.objects.create(model_name='TestData')
        Version.objects.create(model_name='TestMappings')
        Version.objects.create(model_name='TestData')

        
    def test_init_current(self):
        """Testing version initialised with str: 'current'"""

        v = Version(model_name='TestData')
        
        # Test current version
        v.set_version_id('current')
        self.assertEqual(v.version_id,3)
        self.assertEqual(v.status,"current")
        
        # Test current version (blank string)
        v.set_version_id('')
        self.assertEqual(v.version_id,3)
        self.assertEqual(v.status,"current")

        # Test current version (string current version int)
        v.set_version_id('3')
        self.assertEqual(v.version_id,3)
        # TODO: Versions are proposed, current or specific
        # (while records are proposed, current or archived)
        self.assertEqual(v.status,"archived")
    
    def test_init_archived(self):

        v = Version(model_name='TestData')

        # Test current version (string current version int)
        v.set_version_id('1')
        self.assertEqual(v.version_id,1)
        self.assertEqual(v.status,"archived")
    