# Create your models here.

from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.apps import apps

from base.messages import Messages

class Version(models.Model):
    """
    Django table holding meta information on versions for all apps.
    """
    
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
    """
    Abstract class for all our database items.
    """
    
    version_first = models.ForeignKey(Version, 
                                      related_name='%(app_label)s_%(class)s_version_first', 
                                      related_query_name='%(app_label)s_%(class)s_version_first',
                                      on_delete=models.CASCADE, 
                                      null=True, 
                                      blank=True)
    version_last = models.ForeignKey(Version, 
                                     related_name='%(app_label)s_%(class)s_version_last', 
                                     related_query_name='%(app_label)s_%(class)s_version_last',
                                     on_delete=models.CASCADE, 
                                     null=True, 
                                     blank=True)

    
    class Meta:
        abstract = True
    

# IDEA: Add "Change label name" as separate action, to ensure that label names remain unique.
#       Add "Translations" model, so that short and long descriptions of Items can be multi language
#       Preferably link updating of Items to updating of Translations


class ItemModel(AssessModel):
    """
    Abstract class for all our items, consist only of labels.
    """
    
    fields  = [ 'label' ]
    label   = models.CharField(max_length=10)


    def __str__(self):
        return self.label


    def set_id_labels_dicts(self):
        """
        Assign a dictionary of all label/pk pairs for this item model.
        """
        
        ### OBS: Set filter to get only current version items
        queryset = { }
        queryset = self.objects.all()
        for query in queryset:
            self.labels_ids[query.label] = query.id
            self.ids_labels[query.id] = query.label

    
    def get_label(self,item_id):
        """
        Return item label name
        """
        
        # NEED ERROR CHECKING HERE???
        item = self.objects.get(pk=item_id)
        return item.label


    def delete(self,item_id):
        """
        Delete the item by setting version status to archived for item and its keys
        """

        delete_label = self.objects.get(pk=item_id).label
        l = "Deleted label " + delete_label + " in " + self.__name__
        v = Version.objects.create(label=l, model=self.__name__)
        self.objects.filter(id=item_id).update(version_last=v.id)


    def create(self,new_label: str) -> None:
        """
        Create new item with label name and commit to database.
        """

        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        current_labels = list(self.objects.filter(**kwargs).values_list(*['label'], flat=True))
        message = Messages()
        d = { 'new_label': new_label  }
        if new_label in current_labels:
            return message.get('item_create_failure',d) 
        else:
            l = "Created label " + new_label + " in " + self.__name__  
            v = Version.objects.create(label=l, model=self.__name__)
            item = self.objects.create(label=new_label,version_first=v)
            item.save()
            return message.get('item_create_success',d) 


    def upload(self,csv_string: str) -> None:
        """
        Upload items in CSV format and commit to database.
        """        

        duplicates = [ ]
        new_labels = [ ]

        # Read all current items (as defined by version_first and _last)
        # for checking whether the new uploaded labels are duplicates or not
        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        current_labels = list(self.objects.filter(**kwargs).values_list(*['label'], flat=True))
        # Split CSV string assuming no header and first column is label
        lines = csv_string.splitlines()
        for line in lines:
            cells = line.split("\t")
            new_label = cells[0]
            if new_label in current_labels:
                duplicates.append(new_label)
            else:
                new_labels.append(new_label)
        # For all new labels, load to database as current items 
        if new_labels:
            l = "Added new " + self.__name__ + ": " + ", ".join(new_labels)
            v = Version.objects.create(label=l, model=self.__name__)
            for new_label in new_labels:
                item = self.objects.create(label=new_label, version_first=v)
                item.save()
        d = {'new_labels': new_labels, 'duplicates': duplicates, 'model_name': self.__name__ }
        message = Messages()
        return message.get("item_upload_report",d)


    def rename(self, item_id: int, new_label: str) -> str:
        """
        Rename item_id's label to new_label. Return succes/failure message 
        
        Renaming the label has no immediate effect on item__id's in 
        data and choice tables. However, the user must ensure that
        new uploaded data take into account the new label names.
        """
        
        # Get names of current items
        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        current_labels = list(self.objects.filter(**kwargs).values_list(*['label'], flat=True))
        current_item = self.objects.get(pk=item_id)
        current_label = current_item.label 
        d = { 'current_label': current_label, 'new_label': new_label  }
        message = Messages()
        if new_label in current_labels:
            return message.get('item_rename_failure',d) 
        else:
            item = self.objects.get(pk=item_id)
            item.label = new_label
            item.save()
            return message.get('item_rename_success',d) 
    

    def get_current_list_context(self):
        """
        Returns context for listing (item_list.+friends) current items
        """
        
        context = { }
        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        context['field_list'] = ['label']
        context['row_list'] = self.objects.filter(**kwargs)
        context['model_name'] = self.model_name
        return context
    
    
    class Meta:
        abstract = True


class DataModel(AssessModel):
    """
    Abstract class for all our tables containing value data
    Fields consist of ForeignKeys to items and one DecimalField 
    containing the value of that ForeignKey combination.
    """
    
    value       = models.DecimalField(max_digits=1, decimal_places=0)
    replaces_id = models.IntegerField(null=True, blank=True)

    fields = [ ]
    column_field = ""
    field_types = { }
    foreign_ids = { }
    foreign_labels = { }
    size = 0
    dimension = ""
    value_decimal_places = 0
    
    def get_field_types(self):
        """
        Returns a fieldname->fieldtype dict for this model.
        """
        
        field_types = { }
        for field in self.fields:
            field_types[field] = self._meta.get_field(field).get_internal_type()
        return field_types
        
    def get_column_items(self,column_name):
        """
        Returns unique list of all items that are keys in this column.
        """
        
        ### OBS: Set filter to get only current version items
        column_model = apps.get_model('items',column_name.capitalize())
        items = column_model.objects.all().values_list('label', flat=True)
        return list(items)

    def set_foreign_keys(self):
        """
        Load foreignkeys from foreign models for all fields defined 
        as foreign keys.Return error message (string) and field name 
        of id/label (dict).
        """
        
        self.field_types = self.get_field_types(self)
        for field in self.fields:
            if self.field_types[field] == "ForeignKey":
                item_model = self.get_field_model(self,field)
                item_model.set_id_labels_dicts(item_model)
                self.foreign_labels[field] = item_model.ids_labels.copy()
                self.foreign_ids[field] = item_model.labels_ids.copy()

    def labels2ids(self,label_row):
        """
        Input a dict of all foreign keys by labels (+ a value/value entry)
        Transform the labels in the dict to foreign key ids and return.
        """
        
        id_row = { }
        decimal_places = self._meta.get_field('value').decimal_places
        self.set_foreign_keys(self)
        for (field,value) in label_row.items():                
            # The value field is not transformed
            if field == 'value':
                # Make sure to round a potential float to a decimal with 
                # model/field appropriate decimal places
                # OBS: This might be unsafe, as the Decimal object might 
                #      still have precision exceeding the Django table 
                #      precision. Look for better method!
                id_row['value'] = round(Decimal(value),decimal_places)
            # If there is an id (the own id) field it is not transformed
            elif field in ['id','replaces_id','version_first', 'version_last']:
                id_row[field] = value
            elif not field in self.fields:
                raise ValueError("Field name " + field + " is not a field in " + self.__name__)
            elif self.field_types[field] == "ForeignKey": 
                id_row[field+"_id"] = self.foreign_ids[field][value]
                try:
                    pass
                except: 
                    raise ValueError("Unknown label " + value + "cannot be converted to item_id")
            else:
                raise ValueError("Data table field was neither ForeignKey or named 'value'")
        return id_row

    def get_field_model(self,field):
        """
        Return item model object from field name.
        """
        
        try:
            item_model = apps.get_model('items',field.capitalize())
        except:
            raise ValueError("Error in retrieving foreign keys from " + field + 
                             ". Please check label spelling " + 
                             "of foreign key fields in models.py: " +  field)
        return item_model

    def set_size_dimension(self):
        """
        Set integer size (expected number of cells in a 100% dense table) 
        and text string dimension.
        """
        
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
        """
        Return dimension text.
        """
        
        if self.dimension == "":
            self.set_size_dimension(self)
        return self.dimension

    def get_size(self):
        """
        Return dimension size.
        """
        
        if self.size == 0:
            self.set_size_dimension(self)
        return self.size
    
    def get_metric(self):
        """
        Return metric for the table's cell values (e.g. average).
        """
        
        size = self.get_size(self)
        if size > 0:
            table_sum = self.objects.aggregate(Sum('value'))
            return table_sum['value__sum']/size              
        else:
            return 0

    def get_cells(self,version_id):
        """
        Return number of cells in version.
        """
        
        if version_id == None:
            filter_cells = { 'version_first__isnull': True, 'version_last__isnull': True }
            c = self.objects.filter(**filter_cells).count()
        elif version_id.isnumeric():
            filter_cells = { 'version_first__le': version_id, 'version_last__gt': version_id }            
            c = self.objects.filter(**filter_cells).count()
        else:
            c = 0
        return c

    class Meta:
        abstract = True

