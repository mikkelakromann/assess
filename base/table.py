import pandas 
from io import StringIO
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from . models import Version
from base.history import History
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 10:35:07 2018

@author: MIKR
"""


class AssessTable():
    """A table represents a database model, which can be 
    pivoted for input (e.g. CSV upload) or for output (HTML tables)
    AssessTable provides load and save methods"""
    
    def __init__(self,model):
        self.model = model
        self.model_name = self.model._meta.object_name.lower()
        self.version = ""                       # Version of the rows in the dataframe
        self.fields = self.model.fields         # Fields is the model's headers 
        self.key_fields = self.fields.copy()    # Fieldsnames for columns containing foreign keys
        self.key_fields.remove('value')
        self.errors = [ ]                       # List of errors registered
        self.records = [ ]                      # Records list of rows, each row being a field_name/value dict
        self.dataframe = pandas.DataFrame       # Pandas DataFrame for data management
        self.headers = { }                      # Headers are the table's rearranged headers 
        self.rows = [ ]                         # Rows are the table's rearraged records
        self.columns = { }                      # Columns for validation and transformation 
                                                # from/to CSV and Pandas
        
    def load_model(self,version="current",dif=""):
        """Load all relevant rows according to version.
        If diff is true, only the change relative to last version is loaded"""
        # Add __label to query to get text labels from foreign keys instead of __id's
        field_list = [ 'value' ]
        for field in self.fields:
            if field != 'value':
                field_list.append(field + "__label")
        # Add also the database primary key to the dataframe (useful for tracking changes)
        field_list.insert(0,'id')
        # Calcuate filters for picking the desired version of the data
        # Version is string that might be numeric
        kwargs = { }
        if version.isdigit(): 
            v = int(float(version))
            if dif == True:
                kwargs['version_first'] = v
            else:
                kwargs['version_first__lte'] = v
        elif version == 'proposed':
            kwargs['version_first__isnull'] = True
            kwargs['version_last__isnull'] = True
            self.version = "proposed"
        else:
            kwargs['version_first__isnull'] = False
            kwargs['version_last__isnull'] = True
            self.version = "current"
        # Execute query and load into data frame
        order_list = self.key_fields.copy()
        order_list.append('-id')
        query = self.model.objects.filter(**kwargs).values(*field_list).order_by(*order_list)
        self.dataframe = pandas.DataFrame.from_records(query)
        # Remove the __label part from the dataframe column names
        field_list = [ ]
        for field in self.dataframe.columns:
            field_list.append(field.replace("__label",""))
        self.dataframe.columns = field_list
        print("Loaded dataframe from database")
        print(self.dataframe)
        self.remove_previous_duplicates()
        print(self.dataframe)

    def remove_previous_duplicates(self):
        """Remove duplicate entries because of multiple versions of the same row
        (row as defined by combinations of the foreignkey items). The dataframe
        was loaded by descending id's in load_model(), so the first row is the 
        most recent that we want for our dataframe"""
        
        def make_key(row,fields):
            """Lambda function for new key column in dataframe.
            The key is the field names joined by a dash."""
            key_values = []
            for field in fields:
                key_values.append(row[field])
            return "-".join(key_values)

        #            
        # First create a key column with the joined 
        self.dataframe['key'] = self.dataframe.apply(lambda row: make_key(row,self.key_fields), axis=1)
        # Mark rows (column remove: True/False) where the key is equal to the key of last row
        self.dataframe = self.dataframe.assign(remove=self.dataframe ['key'].eq(self.dataframe ['key'].shift()))
        # Remove rows marked as previous duplicates of selected version
        self.dataframe = self.dataframe[self.dataframe.remove == False ]

    def load_csv(self,csv_string,delimiters):
        """Loads a CSV type string into self.dataframe."""
        IObuffer = StringIO(csv_string)
        self.dataframe = pandas.read_csv(IObuffer,**delimiters)
        self.dataframe['id'] = None
        self.version = "proposed"
        print("Loaded dataframe from CSV string")
        print(self.dataframe)
        
    def changed_records(self):
        """Compares records in self.dataframe with the database records,
        and returns a list of only the records that have changed."""
        changed_records = [ ]
        # Calculate which fields that are index fields (ie not the value field)
        index_fields = self.fields.copy()
        index_fields.remove('value')
        # Rows in the pivoted table are dict of tuple/dict pairs 
        # { (idx1,idx2,...): {'value': row value}, (,): { '': }, ... next row }
        kwargs = { 'index':  index_fields, 'values': 'value', 'aggfunc': 'sum' }
        # The updated records come from e.g. CSV upload
        updated_records = self.dataframe.pivot_table(**kwargs).to_dict('index')
        # The existing records come from the database
        self.load_model()
        if self.dataframe.empty:
            existing_records = { }
            existing_ids = { }
        else:             
            kwargs = { 'index':  index_fields, 'values': 'value', 'aggfunc': 'sum' }
            existing_records = self.dataframe.pivot_table(**kwargs).to_dict('index')
            kwargs = { 'index':  index_fields, 'values': 'replaces_id', 'aggfunc': 'sum' }
            self.dataframe.rename(index=str, columns={ 'id': 'replaces_id'}, inplace=True)
            existing_ids = self.dataframe.pivot_table(**kwargs).to_dict('index')
        # key is a tuple of the row indices. updated and existing
        # is a dict of row_keys and dicts of { 'value': values }
        existing_keys = list(existing_records.keys())  
        for key in list(updated_records.keys()):
            updated_value = updated_records[key]['value']
            # Do nothing if the updated record is in the database
            if key in existing_keys and updated_value == existing_records[key]['value']:
                pass
            # Construct a dict of fieldname/values for each changed row and add to changed_records
            else:
                index_dict = zip(index_fields,list(key))
                value_dict = updated_records[key] 
                if key in existing_keys:
                    id_dict = existing_ids[key]
                else:
                    id_dict = { 'replaces_id': None }
                row_dict = dict(index_dict,**value_dict)
                row_dict.update(id_dict)
                changed_records.append(row_dict)
        return changed_records


    def save_dataframe(self):
        """Save contents of data frame to Django model database table."""

        # This is ugly, perhaps refactor into an Error class
        def make_error_message(error_type,record,error_dict):
            return (error_type + " "
                    "when uploading CSV table to " + self.model_name + " " 
                    "in the row["  + " , " + str(record) + "] " 
                    "with the error message " + str(error_dict))

        with transaction.atomic():
            try:            
                for record_with_labels in self.changed_records():
                    record_with_ids = self.model.labels2ids(self.model,record_with_labels)
                    new_record = self.model(**record_with_ids)
                    try:
                        new_record.full_clean()
                    except ValidationError as e:
                        raise ValueError(make_error_message("Validation error",new_record,e))
                    new_record.save()
            except IntegrityError as e:
                raise ValueError(make_error_message("Integrity error",new_record,e))

    def validate_column_headers(self):
        """Validate that the CSV data column headers match the model's field names"""
        pass
        
    def validate_column_data(self):
        """Validate that the columns has the applicable data types and valid foreign keys"""
        pass

    def pivot_1dim(self,column_field):
        """Pivot table according to column field and write rows and headers.
        Assigns self.headers to list of table headers and
        self.rows to dict with table headers as keys."""
        # Calculate indices for the dataframe pivoting and do pivot
        if not column_field in self.fields:
            column_field = self.fields[-2]
        row_fields = self.fields.copy()
        row_fields.remove(column_field)
        row_fields.remove('value')
        kwargs = { 'index': row_fields, 'columns': column_field, 'values': 'value', 'aggfunc': 'sum' }
        if not self.dataframe.empty:
            row_dict = self.dataframe.pivot_table(**kwargs).to_dict('index')
            # pivot_table().to_dict('index') returns dict of (index keys tuple) / { dict of column key/values }
            # Pick apart keys and values to store in two lists per row, then merge two lists into dict with zip
            for index_keys,column_values in row_dict.items():
                field_list = row_fields.copy()
                value_list = list(index_keys)
                for column_key,column_value in column_values.items():
                    field_list.append(column_key)
                    value_list.append(column_value)
                self.rows.append(dict(zip(field_list,value_list)))
            self.headers = row_fields + self.model.get_column_items(self,column_field)

    def commit_rows(self,version_info):
        """"Create new version in version table.
        Set version_begin to version_number and version_end to version_number
        indicating that the new row is current version, and the previous one is not."""
        # Add a new version to the Version table
        version = Version.objects.create(**version_info)
        print('version saved 1st time')
        # New proposed records have version_first Null and version_last Null
        # Convert to current records by setting version_first to new version (and keep version_last to Null)
        filter_propose = { 'version_first__isnull': True, 'version_last__isnull': True }
        update_propose = { 'version_first': version.id }
        # Records that are replaced are mentioned in replaced_id in the new rows
        replaced_ids = self.model.objects.filter(**filter_propose).values_list('replaces_id', flat=True)
        filter_current = { 'pk__in': replaced_ids }
        update_current = { 'version_last': version.id }
        self.model.objects.filter(**filter_current).update(**update_current)
        self.model.objects.filter(**filter_propose).update(**update_propose)
        self.version = "current"
        
        # Get information related to model
        # Size of table is the product of item counts in all dimensions
        version.size = self.model.get_size(self.model)
        # Dimension is a text field describing the item sets spanning the model table 
        version.dimension = self.model.get_dimension(self.model)
        # Model is string model name
        version.model = self.model_name


        # Get information related to table
        filter_cells = { 'version_first__isnull': False, 'version_last__isnull': True }
        # Number of cells is table is count of current rows
        version.cells = self.model.objects.filter(**filter_cells).count()
        # Metric is simple average of current cells
        metric = self.model.objects.filter(**filter_cells).aggregate(Sum('value'))
        if version.cells > 0:
            version.metric = metric['value__sum'] / version.cells 
        else:
            version.metric = 0
        # Number of changes in table is count of updates in this version
        filter_changes = { 'version_first': version.id , 'version_last__isnull': True }
        version.changes = self.model.objects.filter(**filter_changes).count()
        version.save()
        print('version saved 2nd time')
            
    def revert_rows(self):
        """Delete all rows with empty version_begin."""
        pass
    
    def proposed_count(self):
        """Return number of proposed rows."""
        filter_propose = { 'version_first__isnull': True, 'version_last__isnull': True }
        return self.model.objects.filter(**filter_propose).count()

    def get_context(self):
        context = { }
        context['rows'] = self.rows
        context['headers'] = self.headers
        context['model_name'] = self.model_name
        history = History(self.model)
        context['history'] = history.context_data 
        context['version_name'] = self.version
        return context