
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum 

from . keys import Keys
from . history import History
from . models import Version
from . errors import (
    CSVlineWrongCount, CSVheaderNotFound, CSVfieldNotFound, 
    NoItemError, NoFieldError, NotCleanRecord, NoRecordIntegrity )


class AssessCollection():
    """Abstract class for collections of AssessModel objects."""

    def __init__(self,model):
        """Initialise the collection using the AssessModel / Django model
        
        Arguments
            model (object): AssesssModel object for the elements of the collection
        """

        self.model = model                      # Model object

        # Collections support tables with one or more index fields, zero or one
        # column fields and exactly one value field
        # Fields are either an index field or the value field
        self.index_fields = model.index_fields  # list: Index field names
        self.value_field = model.value_field    # String: Value field name

        # column_field should be value_field or an element in index_fields
        self.column_field = model.column_field  # String: Column field name
        
        # Records are kept in a dict with values of model objects 
        # The record dict keys are tuples of the index fields
        self.records = {}                       # Dict of model objects 
        self.records_changed = {}               # Dict of changed model objects
        
        # Lists for rendering table in template: headers is for the template
        # These are set by .pivot_1dim()
        self.headers = []                       # List of header strings
        # The union of item_headers and index_headers is equal to headers
        self.item_headers = []                  # List of item header strings
        self.index_headers = []                 # List of index header strings
        # Each row is a dict with keys from self.header and values from DB
        self.rows = []                          # List of row dicts


    def get_context(self):
        """Get context for printing table, history and navigation links."""
        
        context = {}
        context['table_model_name'] = self.model.__name__.lower()
        if not self.rows == []:
            context['row_list'] = self.rows
            context['header_list'] = self.headers
            context['header_list_index'] = self.index_headers
            context['header_list_items'] = self.item_headers
            history = History(self.model)
            context['history'] = history.context_data 
            context['version_name'] = self.version
        return context



    def set_rows(self,column_field: str) -> None:
        """Pivot table and populate self.rows with table for Django template""" 

        keys = Keys(self.model)
                
        if column_field != "":
            self.column_field = column_field
        indices = {}
        order = []
        for field in self.index_fields:
            if field != self.column_field:
                order.append(field)
                indices[field] = keys.indices_labels[field] 
        # key_combos: dict of list of all combinations of items by column name
        # { col1_name: [item1,item2, ...], col2_name: [itemX,itemX, ...]}
        key_combos = keys.item_combos(order,indices,{})
        # Create list of keys (tuples): [(item1,itemX),(item2,itemX)]
        key_list = list(zip(*key_combos.values()))
        # Create table for template with pivoted table
        self.headers = order + keys.indices_labels[self.column_field]
        self.index_headers = order
        self.item_headers = keys.indices_labels[self.column_field]
        row = {}
        for key in key_list:
            # Create index cells from index field names (order) and key values 
            row = dict(zip(order,key))
            # Create value cells by iterating over items in column_field
            for column_field in self.item_headers:
                # Create a record key tupple for self.records 
                # The order of the key elements must equal self.index_fields
                key = ()
                for index_field in self.index_fields:
                    if index_field in self.column_field:
                        key += (column_field,)
                    else:
                        key += (row[index_field],)
                key += ('value',)
                try:
                    row[column_field] = self.records[key].value
                except:
                    pass
            # When all column_fields are done, the row is done
            self.rows.append(row.copy())


        
    def load(self,version: str, changes: bool ,order=[]) -> None:
        """Load model object fields by version to self.records

        Arguments
            version (str): int digit for archived, "proposed" or "current" 
            order (list): list of Django field names for .order()
            changes (bool): True for version changes, False for full version
        """
        
        # Order is the ordering list of fields, if empty use model.index_fields
        if order == []:
            order = self.model.index_fields
        # Calcuate filters for picking the desired version of the data
        # Version is string that might be numeric
        kwargs = { }
        # Current and archived versions have a not_null version_first
        if version.isdigit(): 
            self.version = version
            v = int(float(version))
            # The difference between versions is tied to that version id only 
            if changes:
                kwargs['version_first'] = v
            # The history of a version might extend back to beginning of
            # time, so we need all less than or equal that version id 
            # We might (easily) get too many entries, so that must be 
            # sorted out afterwards
            else:
                kwargs['version_first__lte'] = v
        # Proposed has version_first and version_last is_null()
        elif version == 'proposed':
            self.version = "proposed"
            # For diffs both first and last must be null
            if changes == True:
                # For diffs we exclude current version using that it has 
                # not version_first is_null()
                kwargs['version_first__isnull'] = True
                kwargs['version_last__isnull'] = True
            else:
                # For views, we blend proposed and current. 
                # Both have version_first is_null()
                kwargs['version_last__isnull'] = True
        # Current is always a view, not a diff, since current can be 
        # composed of many versions.
        else:
            self.version = "current"
            kwargs['version_first__isnull'] = False
            kwargs['version_last__isnull'] = True
        # Execute query and load into data frame
        query = self.model.objects.filter(**kwargs).all().order_by(*order)

        # Create record dict with key being tuple of index fields
        # If records are sorted from lowest to highest id, the record
        # dict will end up having only the one latest record for all versions
        self.records = {}
        for record in query:
            key = record.get_key()
            self.records[key] = record
 
    
    def save_changed_records(self,records: dict) -> None:
        """Filter records that were changed, and save them."""

        self.records_changed = {}
        for (key,new_record) in records.items():
            try:
                old_record = self.records[key].value
                if new_record.value != old_record.value:
                    self.records_changed[key] = new_record
            except:
                self.records_changed[key] = new_record
        self.save()
    
    
    def save(self) -> None:
        """Save proposed records to Django model database table."""

        with transaction.atomic():
            try:            
                for (key,record) in self.records_changed.items():
                    print(record)
                    try:
                        record.full_clean()
                    # Validation errors are caused by out of spec numerical
                    # and string values, and keys to wrong items
                    except ValidationError as error:
                        raise NotCleanRecord(record,error)
                    record.save()
            # Integrity errors are caused by unique constraints and ??
            except IntegrityError as error:
                raise NoRecordIntegrity(record,error)


    def commit_rows(self,version_info: dict) -> None:
        """"Add new DB version, commit DB records version_first=version_id."""
        
        # Add a new version to the Version table
        version = Version.objects.create(**version_info)

        # First update all current records to archived 
        fc = version.kwargs_filter_current()
        uc = version.kwargs_update_current_to_archived()
        self.model.objects.filter(**fc).update(**uc)

        # Then update all proposed records to current
        fp = version.kwargs_filter_proposed()
        up = version.kwargs_update_proposed_to_current()
        self.model.objects.filter(**fp).update(**up)
        self.version = "current"
        
        # Get information related to model
        # Size of table is the product of item counts in all dimensions
        version.size = self.model.get_size(self.model)
        # Dimension is a text field describing the item sets 
        # spanning the model table 
        version.dimension = self.model.get_dimension(self.model)
        # Model is string model name
        version.model = self.model_name

        # Get information related to current table 
        # Number of cells is table is count of current rows
        version.cells = self.model.objects.filter(**fc).count()
        # Metric is simple average of current cells
        metric = self.model.objects.filter(**fc).aggregate(Sum('value'))
        if version.cells > 0:
            version.metric = metric['value__sum'] / version.cells 
        else:
            version.metric = 0
        # Number of changes in table is count of updates in this version
        filter_changes = { 'version_first': version.id , 'version_last__isnull': True }
        version.changes = self.model.objects.filter(**filter_changes).count()
        version.save()
            
    def revert_proposed(self) -> None:
        """Delete all proposed rows (with empty version_begin and version_end)."""
        
        v = Version()
        fp = v.kwargs_filter_proposed()
        self.model.objects.filter(**fp).delete()


    def proposed_count(self) -> int:
        """Return number of proposed rows."""
        
        filter_propose = { 'version_first__isnull': True, 'version_last__isnull': True }
        return self.model.objects.filter(**filter_propose).count()


    class Meta:
        abstract = True
    
