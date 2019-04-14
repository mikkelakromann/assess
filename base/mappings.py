from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum 

from io import StringIO
import pandas 

from . models import Version, AssessModel
from . history import History


class MappingModel(AssessModel):
    """Abstract model class  for instances of a mapping"""
    
    model_type = 'mappings_model'

    def __init__(self):
        self.index_fields = [ ]
        self.value_fields = [ ]
    

    def __str__(self):
        return self.label

    
    def create(self):
        """ """
        pass


    def save(self):
        """ """
        pass


    def update(self):
        """ """
        pass


    class Meta:
        abstract = True


class AssessMappings():
    """Class for handling multiple records in a mapping model."""

    
    def __init__(self, model):
        self.model = model
        self.index_fields = model.index_fields
        self.value_fields = model.value_fields
        self.fields = model.index_fields + model.value_fields
        self.field_items = self.get_field_items()
        self.record_keys = self.get_record_keys()
        self.records = { }


    def get_record_keys(self):
        """Combine field_items to record_keys spanning the entire mapping space"""
        pass


    def get_field_items(self):
        """Return all current field_items for lookup and check of values"""
        # Archived and proposed items should not be used in current mappings
        field_items = { }
        for field_name in self.fields:
            try:
                model = apps.get_model('items',field_name)
            except:
                try: 
                    model = apps.get_model('choices',field_name)
                except:
                    raise NoModelError(field_item,'items or choices')
            query = model.objects.filter(**kwargs)
            field_items[field_name] = query
            

        
    def get_db_records(self,version):
        """Return all records of required version to self.records."""
        pass
    

    def get_csv_records(self,CSVstring,delimiters):
        """Return records parsed from CSV string and error checked."""
        pass


    def validate_column_headers():
        """Validate the headers from the CSV string."""
        pass

    
    def validate_column_data():
        """Validate the column data from the CSV string."""
        pass


    def changed_records():
        """Compare self.records to database records, return dffierence"""
        pass


    def save_records():
        """Save self.records to databse."""
        pass
    
    def commit_rows():
        """Commit proposed rows in database."""
        pass
    
    def revert_proposed():
        """Delete proposed new rows from database."""
        pass
        
    def proposed_count():
        pass