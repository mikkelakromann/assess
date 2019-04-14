from decimal import Decimal
from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum 

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
        
        # Lists for rendering table in template: headers is for the tempa
        # These are set by .pivot_1dim()
        self.headers = []                       # List of header strings
        # The union of item_headers and index_headers is equal to headers
        self.item_headers = []                  # List of item header strings
        self.index_headers = []                 # List of index header strings
        # Each row is a dict with keys from self.header and values from DB
        self.rows = []                          # List of row dicts

        # Lookup dicts for index field names and item ids and item labels
        # These are populated by __set_current_indices_items()
        self.indices_ids_labels = {}    # Dict of dicts {field: {id: label}, }
        self.indices_labels_ids = {}    # Dict of dicts {field: {label: id}, }
        self.indices_labels = {}        # Dict of lists {field: [label, ]}


    def get_context(self):
        """Get context for printing table, version history and navigation links."""
        
        context = {}
        context['table_model_name'] = self.model.__name__.lower()
        if not self.rows == []:
            context['row_list'] = self.rows
            context['header_list'] = self.headers
            context['header_list_index'] = self.index_headers
            context['header_list_items'] = self.item_headers
            history = History(self.model)
            context['history'] = history.context_data 
#            context['version_name'] = self.version
        return context



    # combos(['Piger','Drenge','Lærere'], {'Piger': ['Alberte', 'Liva', 'Harriet'], 'Drenge': ['Luca', 'Louie'], 'Lærere': ['Malou', 'Søren', 'Elisabeth']}, {})
    def __item_combos(self,__order,__indices,__columns):
        """Span out all combination of indices to key dicts
            
            Arguments:
                order: list of str field names for ordering of the columns
                indices: dict of list of items still to be arranged in columns
                columns: dict of list of itmes alreadu arranged in columns
        """

        # indices1 = {f1: [iX,iY]}
        # indices2 = {f2: [iA,iB]}
        # keys = {f3: [i1,i2,i3]}
        # indices12 = {f1: [iX,iY], f2: [iA,iB] }
        # indices123 = {f1: [iX,iY], f2: [iA,iB], f3: [i1,i2,i3] }
        # F(indices2,keys) = {f2: [iA,iA,iA,iB,iB,iB], f3: [i1,i2,i3,i1,i2,i3]}
        # F(indices12,keys) F(indices1,F(indices2,keys))
        # F(indices123,[]) = F(indices12,indices3)

        # The routine rearranges the inputs - make copies
        order = __order.copy()
        indices = __indices.copy()
        columns = __columns.copy() 


        # Arrange to columns if there are more indices
        if len(indices) > 0:
            # Calculate the number of rows in already arranged columns
            if len(columns) > 0:
                # We must have a field name to select a dict item, use first
                first_field_name = list(columns.keys())[0]
                column_length = len(columns[first_field_name])
            else:
                column_length = 1
            # Find next field to arrange, and get its items for a new column
            field = order.pop()
            items = indices.pop(field)
            new_columns = { field: [] }
            # In the new column, the items are repeated with the length of 
            # the already arranged columns 
            for i in items:
                new_columns[field].extend([i]*column_length)
            # The already arranged columns are duplicated with the number 
            # of items in the new column
            for column_name in columns.keys():
                new_columns[column_name] = columns[column_name]*len(items)
            # Recursively call back 
            return self.__item_combos(order,indices,new_columns)
        # If no more indices, we're done doing the arranged columns
        else:
            return columns


    def set_rows(self):
        """Pivot table and populate self.rows with table for Django template""" 

        # Load items for setting template table headers
        # OBS: This loads items for all indices, not only the column_field
        self.__set_current_indices_items()

        indices = {}
        order = []
        for field in self.index_fields:
            if field != self.column_field:
                order.append(field)
                indices[field] = self.indices_labels[field] 
        # key_combos: dict of list of all combinations of items by column name
        # { col1_name: [item1,item2, ...], col2_name: [itemX,itemX, ...]}
        key_combos = self.__item_combos(order,indices,{})
        # Create list of keys (tuples): [(item1,itemX),(item2,itemX)]
        key_list = list(zip(*key_combos.values()))
        # Create table for template with pivoted table
        self.headers = order + self.indices_labels[self.column_field]
        self.index_headers = order
        self.item_headers = self.indices_labels[self.column_field]
        row = {}
        for key in key_list:
            # Create index cells from index field names (order) and key values 
            row = dict(zip(order,key))
            # Create value cells by iterating over items in column_field
            for field in self.item_headers:
                # Thie record key is index_fields + column_field + value_field
                t = key+(field,self.value_field,)
                try:
                    row[field] = self.records[t].value
                except:
                    pass
            # When all column_fields are done, the row is done
            self.rows.append(row.copy())

        
    def load(self,version,changes,order=[]):
        """Get model object fields by version        

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
 
    
    def save_csv(self,csv_string):
        """Check user supplied CSV string for consistency and save to DB

        Arguments
            csv_string (str): multi line CSV string from POST 
            column_field (str): name of column field (item name column headers)
        """
        
        # First split the CSV string into columns: one list per column
        # Column lists are stored in a dict {field_name: column list}
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        try:
            columns = self.__parse_csv_string(self,csv_string,delimiters)
        except CSVlineWrongCount as error:
            return error.message
        
        # CSV value columns might be pivoted with one columns headers 
        # consisting of items from the field column_field 
        # Check that the headers are consistent with items in column_field
        try:
            self.__csv_header_check(columns.keys())
        except CSVheaderNotFound as error: 
            return error.message
        
        # CSV index value fields contains item labels. Check that all 
        # labels can be found as items in the database, and that all 
        # number values conform with the model decimal requirements
        try:
            self.records = self.__columns2records(columns)
        except CSVfieldNotFound as error: 
            return error.message
        
        # Saving the records ought to be safe after these checks.
        # Fall back on general error catching, do no checking
        try:
            self.save()
        except: 
            return "Something went wrong saving your values"
        return "Values saved"


    def save(self):
        """Save records (objects) to Django model database table."""

        with transaction.atomic():
            try:            
                for record in self.records_changed:
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

    def commit_rows(self,version_info):
        """"Add new DB version, commit DB records version_first=version_id
        
        Arguments
            version_info: dict of version info from request.POST
        """
        
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
            
    def revert_proposed(self):
        """Delete all proposed rows (with empty version_begin and version_end)."""
        
        v = Version()
        fp = v.kwargs_filter_proposed()
        self.model.objects.filter(**fp).delete()
    

    def __set_current_indices_items(self):
        """Return dict of lists of all current items that are keys in model."""
        
        # OBS: Trying to return the indices items for specified archied 
        # versions is going to be really messy. Current items are needed for
        # chekcing of user upload data integrity
        for column_name in self.index_fields:
            try:
                # Get the foreign key model items for each index in collection
                column_model = self.model._meta.get_field(column_name).remote_field.model
            except:
                # Bad stuff will happen when self.index_field supplied in 
                # app_name / models.py does not reflect the model's columns
                # ### OBS: Provide better error message from messages.py
                return column_name + "internal error."
            ids_labels = {}
            labels_ids = {}
            labels = []
            v = Version()
            fc = v.kwargs_filter_current()
            print(fc)
            for item in column_model.objects.filter(**fc):
                ids_labels[item.id] = item.label
                labels_ids[item.label] = item.id
                labels.append(item.label)
            # Store the list and dicts in the collection object    
            self.indices_ids_labels[column_name] = ids_labels
            self.indices_labels_ids[column_name] = labels_ids
            self.indices_labels[column_name] = labels


    def __parse_csv_string(self,csv_string,delimiters):
        """Parses CSV string into self.records_changed"""
        
        lines = csv_string.splitlines()
        csv_header = lines.pop(0)
        columns = {}

        # Check that headers in CSV string matches field names in database
        csv_field_names = csv_header.split(delimiters['sep']) 
        self.__set_current_indices_items(self)
        labels_ids = self.indices_labels_id
        db_indices_items = self.indices_labels
        db_item_headers = db_indices_items[self.column_field]
        db_field_names = self.index_fields - self.column_field + db_item_headers 
        for name in csv_field_names:
            if name not in db_field_names:
                raise NoFieldError(name,self.model)

        # Split the CSV string into columns (as lists) and save the column
        # lists in a dict of lists { field_name: [list of cells in column ]}
        # Also check that CSV foreign key labels matches those of DB model
        field_count = db_field_names.count()
        for field_name in db_field_names:
            columns[field_name] = []
        for line in lines:
            cells = line.split("\t")
            if cells.count() != field_count:
                raise CSVlineWrongCount(self.model.app_name,line,csv_header)
            record_key = {}
            record_dict = {}
            value = None
            # Iterate through each field in the CSV header to get 
            # each cell corresponding to the header's field name
            for field_name in csv_field_names:
                cell = cells.pop(0)
                # index_field cells must contain valid foreign key label
                # Check and store the foreign key in temporary record key dict
                if field_name in self.index_fields:
                    if cell in db_indices_items[field_name]:
                        record_key[field_name] = cell
                        record_dict[field_name] = labels_ids[field_name][cell]
                    else:
                        raise NoItemError(cell,self.model.__name)

                # The item_header (not cell value) is part of the record key
                if field_name in db_item_headers:
                    record_key[self.column_field] = field_name
                    record_dict[field_name] = labels_ids[field_name][cell]

                # The value field stores the value of the model object
                if field_name == self.value_field:
                    # Data models stores decimal values
                    if self.model.model_type == 'data_model':
                        cell.replace(delimiters['thousands'],'')
                        cell.replace(delimiters['decimal'],'.')
                        value = Decimal(cell)
                    # Mapping models store foreign key labels, so check item 
                    if self.model.model_type == 'mappings_model':
                        if cell in db_indices_items[field_name]:
                            value = cell
                            record_dict[field_name] = labels_ids[field_name][cell]
                        else:
                            raise NoItemError(cell,self.model.__name)
                # Store CSV value as columns
                columns[field_name].append(value)                
            # Store CSV rows as records (i.e. objects)
            record = self.model(**record_dict)
            key = record_key.values()
            if self.records[key].value != record.value:
                self.records_changed[key] = record 
    

    class Meta:
        abstract = True
    
