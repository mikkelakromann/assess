# Create your models here.

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db import models
from django.db.models import Sum
from django.apps import apps

class Version(models.Model):
    label = models.CharField(max_length=15, default="no title")
    user =  models.CharField(max_length=15, default="no user")
    date =  models.DateTimeField(auto_now_add=True)
    note =  models.CharField(max_length=255, default="no notes")
    model = models.CharField(max_length=64, default="unknown")
    dimension = models.CharField(max_length=255, default="{ ? }")
    size = models.IntegerField(null=True, blank=True)
    cells = models.IntegerField(null=True, blank=True)
    changes = models.IntegerField(null=True, blank=True)
    metric = models.DecimalField(max_digits=16, decimal_places=6,null=True, blank=True)
    status = ""
    links = [ ]
    revert_link = ""
    commit_link = ""
    version_link = ""
    id_link = ""    

    def __str__(self):
        return self.label

    def get_current_version(self):
        latest = self.objects.filter(model=self.model).order_by('-id')[0]
        return latest.id

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
    ids_labels = { }
    labels_ids = { }

    def __str__(self):
        return self.label
        
    def set_id_labels_dicts(self):
        """Returns a dictionary of all label/pk pairs for this item model."""
        id_labels_dict = { }
        queryset = { }
        queryset = self.objects.all()
        for query in queryset:
            self.labels_ids[query.label] = query.id
            self.ids_labels[query.id] = query.label

    class Meta:
        abstract = True

class DataModel(AssessModel):
    """Abstract class for all our tables containing value data
    Fields consist of ForeignKeys to items and one DecimalField 
    containing the value of that ForeignKey combination."""

    version_first = models.ForeignKey(Version, related_name='version_first', on_delete=models.CASCADE, null=True, blank=True)
    version_last = models.ForeignKey(Version, related_name='version_last', on_delete=models.CASCADE, null=True, blank=True)
    replaces_id = models.IntegerField(null=True, blank=True)

    fields = [ ]
    column_field = ""
    field_types = { }
    foreign_ids = { }
    foreign_labels = { }
    size = 0
    dimension = ""

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

    def set_foreign_keys(self):
        """Load foreignkeys from foreign models for all fields defined as foreign keys.
        Return error message (string) and field name of id/label (dict)"""
        self.field_types = self.get_field_types(self)
        for field in self.fields:
            if self.field_types[field] == "ForeignKey":
                item_model = self.get_field_model(self,field)
                item_model.set_id_labels_dicts(item_model)
                self.foreign_labels[field] = item_model.ids_labels.copy()
                self.foreign_ids[field] = item_model.labels_ids.copy()

    def labels2ids(self,label_row):
        """Input a dict of all foreign keys by labels (+ a value/value entry)
        Transform the labels in the dict to foreign key ids and return"""
        id_row = { }
        self.set_foreign_keys(self)
        for (field,value) in label_row.items():                
            # The value field is not transformed
            if field == 'value':
                id_row['value'] = value
            # If there is an id (the own id) field it is not transformed
            elif field in ['id','replaces_id','version_first', 'version_last']:
                id_row[field] = value
            elif not field in self.fields:
                raise ValueError("Field name " + field + " is not a field in " + self.model_name)
            elif self.field_types[field] == "ForeignKey": 
                id_row[field+"_id"] = self.foreign_ids[field][value]
                try:
                    pass
                except: 
                    raise ValueError("Unknown label " + value + "cannot be converted to item_id")
            else:
                raise ValueError("Data table field was neither ForeignKey or named 'value'")
        return id_row

    class Meta:
        abstract = True

    def get_field_model(self,field):
        """Return item model object from field name."""
        try:
            item_model = apps.get_model('items',field.capitalize())
        except:
            raise ValueError("Error in retrieving foreign keys from " + field + 
                             ". Please check label spelling " + 
                             "of foreign key fields in models.py: " +  field)
        return item_model

    def set_size_dimension(self):
        """Set integer size (expected number of cells in a 100% dense table) 
        and text string dimension"""
        self.size = 1
        self.dimension = ""
        dimensions = [ ]
        for field in self.fields:
            if not field == "value":
                item_model = self.get_field_model(self,field)
                s = item_model.objects.all().count()
                dimensions.append(str(s))
                self.size = self.size * s
        self.dimension = "{" + " x ".join(dimensions) + "}"
    
    def get_dimension(self):
        """Return dimension text"""
        if self.dimension == "":
            self.set_size_dimension(self)
        return self.dimension

    def get_size(self):
        """Return dimension size"""
        if self.size == 0:
            self.set_size_dimension(self)
        return self.size
    
    def get_metric(self):
        """Return metric for the table's cell values (e.g. average)"""
        size = self.get_size(self)
        if size > 0:
            table_sum = self.objects.aggregate(Sum('value'))
            print(table_sum)
            return table_sum['value__sum']/size              
        else:
            return 0

    def get_cells(self,version_id):
        """Return number of cells in version"""
        if version_id == None:
            filter_cells = { 'version_first__isnull': True, 'version_last__isnull': True }
            c = self.objects.filter(**filter_cells).count()
        elif version_id.isnumeric():
            filter_cells = { 'version_first__le': version_id, 'version_last__gt': version_id }            
            c = self.objects.filter(**filter_cells).count()
        else:
            c = 0
        return c
