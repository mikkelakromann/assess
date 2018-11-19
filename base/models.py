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
        
    def get_id_labels_dict(self):
        """Returns a dictionary of all label/pk pairs for this item model."""
        id_labels_dict = { }
        queryset = self.objects.all()
        for query in queryset:
            id_labels_dict[query.label] = query.id
        return id_labels_dict

    class Meta:
        abstract = True

class DataModel(AssessModel):
    """Abstract class for all our tables containing value data
    Fields consist of ForeignKeys to items and one DecimalField 
    containing the value of that ForeignKey combination."""
    fields = [ ]
    column_field = ""
    field_types = { }
    foreign_keys = { }

    def get_field_types(self):
        """Returns a fieldname->fieldtype dict for this model."""
        field_types = { }
        for field in self.fields:
            field_types[field] = self._meta.get_field(field).get_internal_type()
        return field_types
        
    def get_column_items(self,column_name):
        """Returns unique list of all items that are keys in this column"""
        column_model = apps.get_model('items',column_name.capitalize())
        items = column_model.objects.all().values_list('label', flat=True)
        return list(items)

    def get_foreign_keys(self):
        """Load foreignkeys from foreign models for all fields defined as foreign keys.
        Return error message (string) and field name of id/label (dict)"""
        for field in self.fields:
            if self.field_types[field] == "ForeignKey":
                try:
                    item_model = apps.get_model('items',field.capitalize())
                    self.foreign_keys[field] = item_model.get_id_labels_dict()
                except:
                    raise ValueError("Error in retrieving foreign keys. Please check label spelling " + 
                                     "of foreign key fields in models.py: " +  field)


    class Meta:
        abstract = True

    