from django.test import TestCase
from .. models import Version,TestItemA, TestItemB, TestItemC, TestData
from .. messages import Messages

class DataModelTestCase(TestCase):
    """Testing Table()."""
    
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
        TestData.objects.create(testitema=self.a1,testitemb=self.b2,testitemc=self.c2,value=4,version_first=self.v1)
        TestData.objects.create(testitema=self.a2,testitemb=self.b1,testitemc=self.c1,value=5,version_first=self.v1)
        TestData.objects.create(testitema=self.a2,testitemb=self.b1,testitemc=self.c2,value=6,version_first=self.v1)
        TestData.objects.create(testitema=self.a2,testitemb=self.b2,testitemc=self.c1,value=7,version_first=self.v1)
        TestData.objects.create(testitema=self.a2,testitemb=self.b2,testitemc=self.c2,value=8,version_first=self.v1)


    def test_IndexView(self):
        """Test IndexView """
        response = self.client.get('/choices/index', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_index.html')
        self.assertTrue(type(response.context['item_links']) is list)
        self.assertTrue(type(response.context['data_links']) is list)
        self.assertTrue(type(response.context['mappings_links']) is list)

    def test_BaseIndexView(self):
        """Test BaseIndexView """
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_index.html')

    def test_TableDisplayView(self):
        """Test TableDisplayView"""
        response = self.client.get('/test/testdata', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '1,000', 'c1_id': 1, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)
        
    def test_TableEditView_GET(self):
        """Test TableEditView"""
        response = self.client.get('/test/testdata/edit', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_edit.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '1,000', 'c1_id': 1, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)
                
    def test_TableEditView_POST_success(self):
        """Test TableEditView"""
        POST = {"('a1', 'b1', 'c1', 'value')": '10' }
        response = self.client.post('/test/testdata/edit/', POST, follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '10,000', 'c1_id': 9, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)

    def test_TableUploadView_GET(self):
        """Test TableUploadView GET"""
        response = self.client.get('/test/testdata/upload/', follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_upload_form.html')
        self.assertEqual(response.context['model_name'],'testdata')
        cfc = [{'label': 'testitema', 'name': 'Testitema'},
               {'label': 'testitemb', 'name': 'Testitemb'},
               {'checked': ' checked', 'label': 'testitemc', 'name': 'Testitemc'},
               {'label': 'value', 'name': 'Value'}]
        self.assertEqual(response.context['column_field_choices'],cfc)

    def test_TableUploadView_POST(self):
        """Test TableUploadView POST"""
        csv_data_string_c = """testitema\ttestitemb\tc1\tc2
a1\tb1\t10\t2"""
        POST = {'csv_string': csv_data_string_c, 'column_field': 'testitemc' }
        response = self.client.post('/test/testdata/upload/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '10,000', 'c1_id': 9, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)

    def test_TableCommitView_GET_success(self):
        """Test TableCommitView GET."""
        # First test with no proposed records, we should get table_display
        response = self.client.get('/test/testdata/commit/', follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '1,000', 'c1_id': 1, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)
        # Then test with a proposed records, we should get table_commit_form
        TestData.objects.create(testitema=self.a2,testitemb=self.b2,testitemc=self.c2,value=9)
        response = self.client.get('/test/testdata/commit/', follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_commit_form.html')
        self.assertTrue(type(response.context['table_commit_heading']) is str)
        self.assertTrue(type(response.context['table_commit_notice']) is str)
        self.assertTrue(type(response.context['i18n_label']) is str)
        self.assertTrue(type(response.context['i18n_user']) is str)
        self.assertTrue(type(response.context['i18n_note']) is str)
        self.assertEqual(response.context['model_name'],'testdata')
        # TODO test failures
        
    def test_TableCommitView_POST_success(self):
        """Test TableCommitView POST."""
        # Commit new record (a1,b1,c1)=10
        TestData.objects.create(testitema=self.a1,testitemb=self.b1,testitemc=self.c1,value=10)
        POST = {'label': 'test label', 'user': 'test user', 'note': 'test note', }
        response = self.client.post('/test/testdata/commit/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        # The table display should have the value 10
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '10,000', 'c1_id': 9, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)
        # TODO test failures
        
    def test_TableRevertView(self):
        """Test TableRevertView."""
        # CReate new proposed record
        TestData.objects.create(testitema=self.a2,testitemb=self.b2,testitemc=self.c2,value=9)
        # Revert the proposed record
        response = self.client.get('/test/testdata/revert/', follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table_display.html')
        self.assertTrue(type(response.context['header_list']) is list)
        self.assertTrue(type(response.context['row_list']) is list)
        self.assertEqual(response.context['table_model_name'],'testdata')
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        self.assertEqual(response.context['errors'],[])
        self.assertEqual(response.context['header_list'], ['testitema','testitemb','c1','c2'])
        # The value of the old record should remain at (a1,b1,c1)=1
        exp_1st_row= {'testitema':'a1', 'testitemb':'b1', 
                      'c1': '1,000', 'c1_id': 1, 'c1_key': "('a1', 'b1', 'c1', 'value')", 
                      'c2': '2,000', 'c2_id': 2, 'c2_key': "('a1', 'b1', 'c2', 'value')" }
        act_1st_row = response.context['row_list'][0]
        self.assertEqual(act_1st_row,exp_1st_row)

    def test_ItemListView(self):
        """Test ItemListView."""
        response = self.client.get('/test/list/testitema/', follow=True )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertTrue(type(response.context['item_header_list']) is list)
        # Listing of items should show all items
        l_exp = ['a1','a2']
        l_act = []
        for o in response.context['item_row_list']:
            l_act.append(o.label)
        self.assertEqual(l_act,l_exp)

    def test_ItemDeleteView_POST_success(self):
        """Test ItemDeleteView POST successful."""
        POST = { 'id': '1' }
        response = self.client.post('/test/delete/testitema/1/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertTrue(type(response.context['item_header_list']) is list)
        # Listing of items should show all items
        l_exp = ['a2']
        l_act = []
        for o in response.context['item_row_list']:
            l_act.append(o.label)
        self.assertEqual(l_act,l_exp)

    # TODO: Make failure tests
    def test_ItemDeleteView_POST_failure(self):
        """Test ItemDeleteView failure."""
        POST = { 'id': '100' }
        POST = {}
#        response = self.client.post('/test/delete/testitema/1/', POST, follow=True)


    def test_ItemDeleteView_GET_success(self):
        """Test ItemDeleteView GET delete form successful."""
        msg = Messages()
        response = self.client.get('/test/delete/testitema/1/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_delete_form.html')
        self.assertEqual(response.context['item_delete_heading'],msg.get('item_delete_heading', {'delete_item': 'a1', 'model_name': 'TestItemA'}))
        self.assertEqual(response.context['item_delete_notice'],msg.get('item_delete_notice', {}))

    def test_ItemUpdateView_POST_success(self):
        """Test ItemDeleteView POST successful."""
        POST = { 'id': '1', 'label': 'a0' }
        response = self.client.post('/test/update/testitema/1/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertTrue(type(response.context['item_header_list']) is list)
        # Listing of items should show all items
        l_exp = ['a0', 'a2']
        l_act = []
        for o in response.context['item_row_list']:
            l_act.append(o.label)
        self.assertEqual(l_act,l_exp)

    # TODO: Make failure tests
    def test_ItemUpdateView_POST_failure(self):
        """Test ItemDeleteView failure."""
        POST = { 'id': '100' }
        POST = {}
#        response = self.client.post('/test/delete/testitema/1/', POST, follow=True)
    
    def test_ItemUpdateView_GET(self):
        """Test ItemDeleteView GET delete form successful."""
        msg = Messages()
        response = self.client.get('/test/update/testitema/1/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_update_form.html')
        self.assertEqual(response.context['item_update_heading'],msg.get('item_update_heading', {'current_label': 'a1', 'model_name': 'TestItemA'}))
        self.assertEqual(response.context['item_update_new_label'],msg.get('item_update_new_label', {'current_label': 'a1'}))

    def test_ItemCreateView_POST_success(self):
        """Test ItemDeleteView POST successful."""
        msg = Messages()
        POST = { 'label': 'a3' }
        response = self.client.post('/test/create/testitema/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertTrue(type(response.context['item_header_list']) is list)
        self.assertEqual(response.context['item_list_message'],msg.get('item_create_success', {'new_label': 'a3'}))
        # Listing of items should show all items
        l_exp = ['a1', 'a2', 'a3' ]
        l_act = []
        for o in response.context['item_row_list']:
            l_act.append(o.label)
        self.assertEqual(l_act,l_exp)

    def test_ItemCreateView_GET(self):
        """Test ItemDeleteView GET delete form successful."""
        msg = Messages()
        response = self.client.get('/test/create/testitema/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_create_form.html')
        self.assertEqual(response.context['item_create_heading'],msg.get('item_create_heading', {'current_label': 'a1', 'model_name': 'TestItemA'}))
        self.assertEqual(response.context['item_new_label'],msg.get('item_new_item_label', {'current_label': 'a1'}))
        
    def test_ItemUploadView_POST_success(self):
        """Test ItemDeleteView POST successful."""
        msg = Messages()
        POST = { 'CSVstring': 'a3\na4' }
        response = self.client.post('/test/upload/testitema/', POST, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertTrue(type(response.context['item_header_list']) is list)
        self.assertEqual(response.context['item_list_message'],msg.get('item_upload_report', {'new_labels': ['a3','a4'], 'duplicates': [], 'model_name': 'TestItemA'}))
        # Listing of items should show all items
        l_exp = ['a1', 'a2', 'a3', 'a4' ]
        l_act = []
        for o in response.context['item_row_list']:
            l_act.append(o.label)
        self.assertEqual(l_act,l_exp)

    def test_ItemUploadView_GET(self):
        """Test ItemUploadView GET delete form successful."""
        msg = Messages()
        response = self.client.get('/test/upload/testitema/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_upload_form.html')
        self.assertEqual(response.context['item_list_heading'], msg.get('item_list_heading',{ 'model_name': 'TestItemA'}))
        self.assertEqual(response.context['model_name'], 'testitema')
#        self.assertEqual(response.context['item_new_label'],msg.get('item_new_item_label', {'current_label': 'a1'}))
        
    