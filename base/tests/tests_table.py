from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from base.models import Version,TestItemA, TestItemB, TestItemC, TestData
from base.table import AssessTable
from base.errors import NotDecimalError, NoFieldError, KeyNotFound, NotCleanRecord


class TableTestCase(TestCase):
    """Testing Table()."""
    
    def setUp(self):
        self.context = []
        v1 = Version()
        v1.set_version_id("1")
        v1.save()
        v2 = Version()
        v2.set_version_id("2")
        v2.save()

        self.v1 = v1
        self.v2 = v2
    
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

        self.a1 = a1
        self.a2 = a2
        self.b1 = b1
        self.b2 = b2
        self.c1 = c1
        self.c2 = c2

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


    def test_get_version_metric(self):
        """Test the history context (list of versions)."""
        t = AssessTable(TestData, "current")
        t.load(False)
        vd = t.get_version_metric()
        self.assertEqual(vd['model_name'],'testdata')
        self.assertEqual(vd['size'],8)
        self.assertEqual(vd['dimension'],'{2 x 2 x 2}')
        self.assertEqual(vd['metric'],sum([1,2,3,4,5,6,7,8])/8)
        self.assertEqual(vd['cells'],8)
        self.assertEqual(vd['changes'],4)



    def test_table_save_POST_success(self):
        """Test saving data using POST edit method."""
        t = AssessTable(TestData, "")
        t.load(False,[])
        POST = {"('a1', 'b1', 'c1', 'value')": '10', "('a1', 'b1', 'c2', 'value')": '11',  }
        t.save_POST(POST)        
        # Test no errors and that other records were unchanged
        self.assertEqual(t.errors,[])
        self.assertEqual(t.records[('a1','b2','c1','value')].get_value(), '3,000')
        # Load proposed and test that the changes took effect
        t = AssessTable(TestData, "proposed")
        t.load(False,[])
        self.assertEqual(t.records[('a1','b1','c1','value')].get_value(), '10,000')
        self.assertEqual(t.records[('a1','b1','c2','value')].get_value(), '11,000')

    def test_table_save_POST_failure(self):
        """Test failure when saving data using POST edit method."""
        t = AssessTable(TestData, "")
        t.load(False,[])
        # Test bad decimal
        POST = {"('a1', 'b1', 'c1', 'value')": 'bad_decimal'  }
        t.save_POST(POST)        
        self.assertEqual(str(t.errors.pop()),str(NotDecimalError('bad_decimal',TestData)))
        self.assertEqual(t.records[('a1','b1','c1','value')].get_value(), '1,000')
        # Test bad POST key - item label
        POST = {"('bad_item', 'b1', 'c1', 'value')": '1'  }
        t.save_POST(POST)        
        self.assertEqual(str(t.errors.pop()),str(KeyNotFound("bad_item in ('bad_item', 'b1', 'c1', 'value')", TestData)))
        self.assertEqual(t.records[('a1','b1','c1','value')].get_value(), '1,000')
        # Test bad value field
        POST = {"('a1', 'b1', 'c1', 'bad_value_field')": '1'  }
        t.save_POST(POST)        
        self.assertEqual(str(t.errors.pop()),str(NoFieldError('bad_value_field', TestData)))
        self.assertEqual(t.records[('a1','b1','c1','value')].get_value(), '1,000')
        # TODO: We need to test thoroughly decimal punctuation, that need to be dynamic and it is not yet ...

    def test_table_save_CSV_success(self):
        """Test saving of data model through CSV"""
        t = AssessTable(TestData, "")
        t.load(False,[])
        # Test bad decimal
        csv_string = "testitema\ttestitemb\ttestitemc\tvalue\na1\tb1\tc1\t10"
        POST = { 'csv_string': csv_string, 'column_field': 'value' }
        t.save_CSV(POST)        
        t = AssessTable(TestData, "proposed")
        t.load(False,[])
        self.assertEqual(t.errors,[])
        self.assertEqual(t.records[('a1','b1','c1','value')].get_value(), '10,000')

    def test_table_get_CSV_form_context(self):
        """Test get CSV form context."""
        t = AssessTable(TestData, "")
        context = t.get_CSV_form_context()
        column_field_choices = [ 
                {'label': 'testitema', 'name': 'Testitema'},
                {'label': 'testitemb', 'name': 'Testitemb'},
                {'checked': ' checked', 'label': 'testitemc', 'name': 'Testitemc'},
                {'label': 'value', 'name': 'Value'} ]
        self.assertEqual(context['column_field_choices'],column_field_choices)
        self.assertEqual(context['model_name'],'testdata')

    def test_table_save_changed_records_success(self):
        """Test save_changed_records. """
        record_dict = {'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'value': '10,000'}
        r = TestData()
        r.set_fk_labels_objects()
        r.set_from_record_dict(record_dict)
        # First test modifying an existing record
        t = AssessTable(TestData, "")
        t.load(False,[])
        t.changed_records = { r.get_key(): r }
        t.save_changed_records(t.changed_records)
        t = AssessTable(TestData, "proposed")
        # Load proposed records
        t.load(False,[])
        self.assertEqual(t.records[r.get_key()], r)
        # Then delete the old (id=1) new record (id=13) and insert it to test insertion as well
        TestData.objects.filter(id=1).delete()
        TestData.objects.filter(id=13).delete()
        t.load(False,[])
        t.changed_records = { r.get_key(): r }
        t.save_changed_records(t.changed_records)
        t = AssessTable(TestData, "proposed")
        # Load proposed records
        t.load(False,[])
        self.assertEqual(t.records[r.get_key()].value, r.value)

    def test_table_save_changed_records_failure(self):
        """Test save_changed_records. """
        # First test modifying an existing record
        t = AssessTable(TestData, "")
        t.load(False,[])
        r = TestData.objects.get(id=1)
        r.value = "bad_decimal_value"
        t.changed_records = { r.get_key(): r }
        try:
            t.save_changed_records(t.changed_records)
        except NotCleanRecord as e1:
            r2 = TestData.objects.get(id=1)
            r2.value =  "bad_decimal_value"
            try:
                r2.full_clean()
            except ValidationError as e3:
                self.assertEqual(str(e1),str(NotCleanRecord(r,e3)))

    def test_table_commit_form_context(self):
        """Test that all elements in context is present."""
        
        key_list1 = ['table_commit_heading', 'table_commit_notice', 
             'table_commit_submit', 'i18n_user', 'i18n_label', 'i18n_note', 
             'table_commit_notable']
        t = AssessTable(TestData, "")
        context = t.get_commit_form_context()
        key_list2 = context.keys()
        for e in key_list1:
            self.assertIn(e, key_list2)

    def test_table_commit_success(self):
        """Test saving data using POST edit method."""
        t = AssessTable(TestData, "")
        t.load(False,[])
        POST = {"('a1', 'b1', 'c1', 'value')": '10', "('a1', 'b1', 'c2', 'value')": '11',  }
        t.save_POST(POST)        
        # Test no errors and that other records were unchanged
        self.assertEqual(t.errors,[])
        self.assertEqual(t.records[('a1','b2','c1','value')].value, Decimal('3'))
        # Load proposed and test that the changes took effect
        version_info = {'label': 'new', 'user': 'mikr', 'note': 'haha' }
        t.commit_rows(version_info)
        t.load(False,[])
        self.assertEqual(t.records[('a1','b1','c1','value')].value, Decimal('10'))
        self.assertEqual(t.records[('a1','b1','c2','value')].value, Decimal('11'))

    def test_table_revert(self):
        """Test revert table functionality."""
        # In our setup, we have 12 records
        self.assertEqual(TestData.objects.count(),12)
        # Then add one proposed record - we now have 13
        t = AssessTable(TestData, "")
        t.load(False,[])
        POST = {"('a1', 'b1', 'c1', 'value')": '99',  }
        t.save_POST(POST)        
        self.assertEqual(TestData.objects.count(),13)
        # Then revert the new proposed record, now we're back to 12 again
        t.revert_proposed()
        self.assertEqual(TestData.objects.count(),12)
        
    def test_counnt_proposed(self):
        """Test count proposed functionality."""
        # In our setup, we have 12 records
        self.assertEqual(TestData.objects.count(),12)
        # Then add one proposed record - we now have 13
        t = AssessTable(TestData, "")
        t.load(False,[])
        POST = {"('a1', 'b1', 'c1', 'value')": '99',  }
        t.save_POST(POST)      
        self.assertEqual(t.proposed_count(),1)
        

#    def test_table_load_all(self):
#        """Test load current, all records"""
#        t = AssessTable(TestData, "")
#        # First load current version, all records
#        t.load(False,[])
#        v = t.version
#        proposed_values = [1,2,3,4,5,6,7,8]
#        v.set_metrics(TestData,proposed_values)
#        self.assertEqual(v.version_id,2)
#        self.assertEqual(v.cells,8)
#        self.assertEqual(v.size,8)
#        self.assertEqual(v.dimension,'{2 x 2 x 2}')
#        avg = (1+2+3+4+5+6+7+8)/8
#        self.assertEqual(v.metric,avg)
#        # TODO: Changes ought probably to be calculated as version_first = v2 
#        # and not all records in current version. This is a set_metrics problem
#        # Perhaps set_metrics ought to belong in table doing stuff on 
#        # AssessTable.records rather than directly from the database?
##        self.assertEqual(v.changes,8)
#
#    def test_table_load_changes(self):
#        """Test load current, changed records"""
#        t = AssessTable(TestData, "")
#        t.load(True,[])
#        v = t.version
#        proposed_values = []
#        v.set_metrics(TestData,proposed_values)
#        self.assertEqual(v.version_id,2)
#        self.assertEqual(v.cells,8)
#        self.assertEqual(v.size,8)
#        self.assertEqual(v.dimension,'{2 x 2 x 2}')
#        avg = (3+4+7+8)/4
#        avg = (1+2+3+4+5+6+7+8)/8
##        self.assertEqual(v.metric,avg)
#        # TODO: Changes ought probably to be calculated as version_first = v2 
#        # and not all records in current version. This is a set_metrics problem
#        # Perhaps set_metrics ought to belong in table doing stuff on 
#        # AssessTable.records rather than directly from the database?
##        self.assertEqual(v.changes,4)

