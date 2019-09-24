from django.test import TestCase
from base.models import Version,TestItemA, TestItemB, TestItemC
from base.set import AssessSet
from base.messages import Messages

csv_str_2new = "a3\na4"
csv_str_1new1old = "a2\na3"
csv_str_2old = "a1\na2"


class TableDataTestCase(TestCase):
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
        TestItemB.objects.create(label='b1',version_first=v1, version_last=v2)
        TestItemB.objects.create(label='b2',version_first=v1)
        TestItemC.objects.create(label='c1',version_first=v1)
        TestItemC.objects.create(label='c2',version_first=v1)

        self.a1 = TestItemA.objects.get(label='a1')
        self.a2 = TestItemA.objects.get(label='a2')
        self.b1 = TestItemB.objects.get(label='b1')
        self.b2 = TestItemB.objects.get(label='b2')
        self.c1 = TestItemC.objects.get(label='c1')
        self.c2 = TestItemC.objects.get(label='c2')

    def test_set_init_(self):
        """Test initialisation of AssessSet."""
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1','a2'])        
        self.assertEqual(s.labels_by_ids, { 1: 'a1', 2: 'a2' })
        self.assertEqual(s.ids_by_labels, { 'a1': 1, 'a2': 2 })
        self.assertEqual(s.items, { 'a1': self.a1, 'a2': self.a2 })

    def test_set_init_archived(self):
        """Test initialisation of AssessSet with an archived item."""
        s = AssessSet(TestItemB)
        # The archived item should not be loaded into the set
        self.assertEqual(s.labels,['b2'])        
        self.assertEqual(s.labels_by_ids, { 2: 'b2' })
        self.assertEqual(s.ids_by_labels, { 'b2': 2 })
        self.assertEqual(s.items, { 'b2': self.b2 })

    def test_set_delete_success(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.delete("1")
        msg = 'SUCCESS: Deleted item a1 in TestItemA.'
        self.assertEqual(s.context['item_list_message'], msg)
        # Test that item a1 was in fact deleted
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a2'])        
        self.assertEqual(s.labels_by_ids, { 2: 'a2' })
        self.assertEqual(s.ids_by_labels, { 'a2': 2 })
        self.assertEqual(s.items, { 'a2': self.a2 })
        
    def test_set_delete_fail(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.delete("bad_item_id_str")
        msg = "ERROR: Cannot delete item #bad_item_id_str in TestItemA - " + \
            "it does not exist."
        self.assertEqual(s.context['item_list_message'], msg)

    def test_set_delete_form_success(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.get_delete_form_context("1")
        msg = "Delete item a1 in TestItemA:"
        self.assertEqual(s.context['item_delete_heading'], msg)
        self.assertNotEqual(s.context['item_delete_notice'], '')
        self.assertNotEqual(s.context['item_delete_confirm'], '')
        self.assertNotEqual(s.context['item_delete_reject'], '')
        
    def test_set_delete_form_fail(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.get_delete_form_context("bad_item_id_str")
        msg = "ERROR: Cannot delete item #bad_item_id_str in TestItemA - " + \
            "it does not exist."
        self.assertNotEqual(s.context['item_delete_heading'], '')
        self.assertEqual(s.context['item_delete_failure'], msg)

    def test_set_create_success(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.create("a3")
        msg = 'SUCCESS: Created item a3.'
        self.assertEqual(s.context['item_list_message'], msg)
        self.a3 = TestItemA.objects.get(label='a3')
        # Test that item a1 was in fact deleted
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2', 'a3'])        
        self.assertEqual(s.labels_by_ids, { 1: 'a1', 2: 'a2', 3: 'a3' })
        self.assertEqual(s.ids_by_labels, { 'a1': 1, 'a2': 2, 'a3': 3 })
        self.assertEqual(s.items, { 'a1': self.a1, 'a2': self.a2, 'a3': self.a3 })

    def test_set_create_fail(self):
        """Test create expected failure."""
        # We should not be able to create existing labels
        s = AssessSet(TestItemA)
        s.create("a1")
        msg = "ERROR: Could not create item a1, as this name is used by another item."
        self.assertEqual(s.context['item_list_message'], msg)
        # Maximum label length is 10 characters
        s = AssessSet(TestItemA)
        s.create("a1234567890")
        msg = "ERROR: Could not create item a1234567890, as this name is longer than 10 characters."
        self.assertEqual(s.context['item_list_message'], msg)

    def test_set_Create_form_success(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.get_create_form_context()
        msg = Messages()
        d = { 'model_name': s.name }
        self.assertEqual(s.context['item_new_label'], msg.get('item_new_item_label', d))
        self.assertEqual(s.context['item_create_heading'], msg.get('item_create_heading', d))
        self.assertEqual(s.context['item_create_text'], msg.get('item_create_text', d))
        self.assertEqual(s.context['item_create_confirm'], msg.get('item_create_confirm', d))
        self.assertEqual(s.context['item_create_reject'], msg.get('item_create_reject', d))
        
    def test_set_upload_2old(self):
        """Test  set.upload)() for successful cases."""
        # Try to load a1 and a2 into TestItemA, none should be added
        msg = Messages()
        s = AssessSet(TestItemA)
        s.upload_csv(csv_str_2old)
        d = {'new_labels': [], 'duplicates': ['a1', 'a2'], 'model_name': s.name }
        self.assertEqual(s.context['item_list_heading'], msg.get("item_upload_heading",d))
        self.assertEqual(s.context['item_list_message'], msg.get("item_upload_report",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2'])        

    def test_set_upload_1old1new(self):
        """Test  set.upload)() for successful cases."""
        # Try to load a2 and a3 into TestItemA, only a3 should be added
        msg = Messages()
        s = AssessSet(TestItemA)
        s.upload_csv(csv_str_1new1old)
        d = {'new_labels': ['a3'], 'duplicates': ['a2'], 'model_name': s.name }
        self.assertEqual(s.context['item_list_heading'], msg.get("item_upload_heading",d))
        self.assertEqual(s.context['item_list_message'], msg.get("item_upload_report",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2', 'a3'])        
        s = AssessSet(TestItemA)

    def test_set_upload_2new(self):
        """Test  set.upload)() for successful cases."""
        # Try to load a3 and a4 into TestItemA, both should be added
        msg = Messages()
        s = AssessSet(TestItemA)
        s.upload_csv(csv_str_2new)
        d = {'new_labels': ['a3', 'a4'], 'duplicates': [], 'model_name': s.name }
        self.assertEqual(s.context['item_list_heading'], msg.get("item_upload_heading",d))
        self.assertEqual(s.context['item_list_message'], msg.get("item_upload_report",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2', 'a3', 'a4'])        
                
    def test_set_update_success(self):
        """Test  set.update() for successful cases."""
        # Try to rename a1 to a3 in TestItemA, should be success
        msg = Messages()
        s = AssessSet(TestItemA)
        POST = { 'id': '1', 'label': 'a3' }
        s.update(POST)
        d = {'current_label':'a1', 'new_label': 'a3' }
        self.assertEqual(s.context['item_list_message'], msg.get("item_update_success",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a3', 'a2'])        
                
    def test_set_update_fail_duplicate(self):
        """Test  set.update() for successful cases."""
        # Try to rename a1 to a2 in TestItemA, should fail as a2 exists
        msg = Messages()
        s = AssessSet(TestItemA)
        POST = { 'id': '1', 'label': 'a2' }
        s.update(POST)
        d = {'current_label':'a1', 'new_label': 'a2' }
        self.assertEqual(s.context['item_list_message'], msg.get("item_update_failure",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2'])        
                
    def test_set_update_fail_ID(self):
        """Test  set.update() for successful cases."""
        # Try to rename a1 to a2 in TestItemA, should fail as a2 exists
        msg = Messages()
        s = AssessSet(TestItemA)
        POST = { 'id': '3', 'label': 'a2' }
        s.update(POST)
        d = {'item_id': '3', 'new_label': 'a2' }
        self.assertEqual(s.context['item_list_message'], msg.get("item_update_fail_ID",d))
        # Reload and check whether the new items were addded
        s = AssessSet(TestItemA)
        self.assertEqual(s.labels,['a1', 'a2'])        

    def test_set_update_form_success(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.get_update_form('1')
        msg = Messages()
        d = { 'model_name': s.name, 'current_label': 'a1'  }
        self.assertEqual(s.context['item_update_id'], 1)
        self.assertEqual(s.context['item_update_heading'], msg.get('item_update_heading', d))
        self.assertEqual(s.context['item_update_new_label'], msg.get('item_update_new_label', d))
        self.assertEqual(s.context['item_update_confirm'], msg.get('item_update_confirm', d))
        self.assertEqual(s.context['item_update_reject'], msg.get('item_update_reject', d))

    def test_set_update_form_failure(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        s.get_update_form('3')
        msg = Messages()
        d = { 'model_name': s.name, 'item_id': '#3', 'new_label': 'new label', 'current_label': 'current label'  }
        self.assertEqual(s.context['item_update_heading'], msg.get('item_update_heading', d))
        self.assertEqual(s.context['item_update_failure'], msg.get('item_update_fail_ID', d))


    def test_set_get_context(self):
        """Test successfull delete."""
        s = AssessSet(TestItemA)
        context = s.get_context()
        msg = Messages()
        d = { 'model_name': s.name }
        query = [self.a1, self.a2]
        self.assertEqual(context['item_list_heading'], msg.get('item_list_heading',d))
        self.assertEqual(context['item_list_no_items'], msg.get('item_list_no_items',{}))
        self.assertEqual(list(context['item_row_list']), query)
        self.assertEqual(context['item_header_list'], ['label'])
