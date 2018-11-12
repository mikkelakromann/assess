# Create your models here.

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db import models
from django.apps import apps

class Version(models.Model):
    label =  models.CharField(max_length=15)
    user =  models.CharField(max_length=15)
    date =   models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

class AssessModel(models.Model):

    fields = [ ]
    model_name = "unknown"

    def get_field_types(self):
        """Returns a fieldname->fieldtype dict for this model."""
        field_types = { }
        for field in self.fields:
            field_types[field] = self._meta.get_field(field).get_internal_type()
        return field_types
        
    def get_id_labels_dict(self):
        """Returns a dictionary of all label/pk pairs for this model."""
        id_labels_dict = { }
        queryset = self.objects.all()
        for query in queryset:
            id_labels_dict[query.label] = query.id
        return id_labels_dict


# NOTE: If label exists already, we should update the row instead of inserting a new
#       Thus we will avoid breaking primary key relations to other tables
#       How about excessive existing DB rows that are not in the CSV rows - should probably be deleted with cascading effect
#       Perhaps consider to shift the burden of integer primary key to the user?
#       This problem is perhaps only present for "items", but not for other model types?
#       Consider adding a check whether the label already exists - 
#       Then add existing labels to one list, and new labels to another
#       Do not add rows where data is identical to existing DB rows 
    @classmethod
    def import_rows(model_class,import_rows):
        """Import a list of rows (each a fieldnames/values dict) into the database."""
        
        # This is ugly, perhaps refactor into an Error class
        def make_error_message(error_type,model_name,row,error_dict):
            return (error_type + " "
                    "when uploading CSV table to " + model_name + " " 
                    "in the row["  + " , ".join(row) + "] " 
                    "with the error message " + str(error_dict))

        with transaction.atomic():
            try:            
                for import_row in import_rows:
                    new_record = model_class(**import_row)
                    try:
                        new_record.clean_fields()
                        new_record.clean()
                        new_record.validate_unique()
                    except ValidationError as e:
                        raise ValueError(make_error_message("Validation error",new_record.model_name,import_row,e))
    
                    new_record.save()
            except IntegrityError as e:
                raise ValueError(make_error_message("Integrity error",new_record.model_name,import_row,e))
   
    def commit_rows(self):
        """"Set version_begin to version_number and version_end to version_number
        indicating that the new row is current version, and the previous one is not."""
        pass
    
    def revert_rows(self):
        """Delete all rows with empty version_begin."""
        pass
    
    def current_rows(self):
        pass
    
    class Meta:
        abstract = True
    

# IDEA: Add "Change label name" as separate action, to ensure that label names remain unique.
#       Add "Translations" model, so that short and long descriptions of Items can be multi language
#       Preferably link updating of Items to updating of Translations

class ItemModel(AssessModel):
    """Abstract class for all our items, consist only of labels"""
    fields  = [ 'label' ]
    label   = models.CharField(max_length=10)

    def __str__(self):
        return self.label
        
    class Meta:
        abstract = True

class DataModel(AssessModel):
    """Abstract class for all our tables containing value data
    Fields consist of ForeignKeys to items and one DecimalField 
    containing the value of that ForeignKey combination."""
    fields = [ ]
    column_field = ""
        
    def __str__(self):
        return self.label
        
    def get_column_items(self,column_name):
        """Returns unique list of all items that are keys in this column"""
        column_model = apps.get_model('items',column_name.capitalize())
        return list(column_model.objects.values('label'))

    class Meta:
        abstract = True
