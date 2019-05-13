from django.db import models

from . messages import Messages
from . version import Version

class AssessModel(models.Model):
    """Abstract class for all our database items."""
    
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
    """Abstract class for all our items, consist only of labels."""

    model_type = 'item_model'    
    label   = models.CharField(max_length=10)


    def __str__(self):
        return self.label


#    def set_id_labels_dicts(self):
#        """Assign a dictionary of all label/pk pairs for this item model."""
#        
#        ### OBS: Set filter to get only current version items
#        self.labels_ids = { }
#        self.ids_labels = { }
#        queryset = { }
#        queryset = self.objects.all()
#        for query in queryset:
#            self.labels_ids[query.label] = query.id
#            self.ids_labels[query.id] = query.label
#
#    
    def get_label(self,item_id):
        """Return item label name"""
        
        # NEED ERROR CHECKING HERE???
        item = self.objects.get(pk=item_id)
        return item.label


    def delete(self,item_id):
        """Delete the item by setting version status to archived for item and its keys"""

        delete_label = self.objects.get(pk=item_id).label
        l = "Deleted label " + delete_label + " in " + self.__name__
        v = Version.objects.create(label=l, model=self.__name__)
        self.objects.filter(id=item_id).update(version_last=v.id)
        ### OBS! Also set "archived" for all maps and tables using item???


    def create(self,new_label: str) -> None:
        """Create new item with label name and commit to database."""

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
        """Upload items in CSV format and commit to database."""        

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
            v = Version.objects.create(label=l)
            for new_label in new_labels:
                item = self.objects.create(label=new_label, version_first=v)
                item.save()
        d = {'new_labels': new_labels, 'duplicates': duplicates, 'model_name': self.__name__ }
        message = Messages()
        return message.get("item_upload_report",d)


    def rename(self, item_id: int, new_label: str) -> str:
        """Rename item_id label to new_label. Return succes/failure message""" 
        
        # Renaming the label has no immediate effect on item__id's in 
        # data and choice tables. However, the user must ensure that
        # new uploaded data take into account the new label names.
        
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
        """Returns context for listing (item_list.+friends) current items"""
        
        context = { }
        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        context['item_header_list'] = ['label']
        # must return list of dicts: [ { 'label': item_label }, { 'label': item_label }, ... ]
        context['item_row_list'] = self.objects.filter(**kwargs)
        context['item_model_name'] = self.model_name
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
    # Why is this field necessary - perhaps obsolete after dropping pandas?
    # Consider using replaces_id (new record point to old record)
    # rather than replaced_id (old record pointing to new record)
#    replaces_id = models.IntegerField(null=True, blank=True)

    model_type = 'data_model'    
 
    # Consider moving this definition inside collection.py, only place its used
    # OBS: Now also used in tableIO.py ... perhaps smart choice, since we can 
    #      then change key everywhere in one go
    def get_key(self):
        keys = []
        for field in self.index_fields:
            keys.append(str(getattr(self,field)))
        keys.append(self.value_field)
        return tuple(keys)        
    
    
#    def get_field_types(self):
#        """
#        Returns a fieldname->fieldtype dict for this model.
#        """
#        
#        field_types = { }
#        app_names = { }
#        for field in self.fields:
#            field_types[field] = self._meta.get_field(field).get_internal_type()
#            app_names[field] = self._meta.app_label
#        return field_types
        
#    def get_column_items(self,column_name):
#        """
#        Returns unique list of all items that are keys in this column.
#        """
#        
#        ### OBS: Perhaps filter to get only current version items or whichever
#        ###      version that might be needed? (ouch!)
#        ###      Perhaps retire this function as it is unreliable and 
#        ###      possibly unnecessary?
#        column_model = self._meta.get_field(column_name).remote_field.model
#        items = column_model.objects.all().values_list('label', flat=True)
#        return list(items)

#    def set_foreign_keys(self):
#        """Load foreignkeys from foreign models for all foreignkey fields."""
#        
#        self.field_types = self.get_field_types(self)
#        for field in self.fields:
#            if self.field_types[field] == "ForeignKey":
#                item_model = self.get_field_model(self,field)
#                item_model.set_id_labels_dicts(item_model)
#                self.foreign_labels[field] = item_model.ids_labels.copy()
#                self.foreign_ids[field] = item_model.labels_ids.copy()
#
#    def labels2ids(self,label_row):
#        """
#        Input a dict of all foreign keys by labels (+ a value/value entry)
#        Transform the labels in the dict to foreign key ids and return.
#        """
#        
#        id_row = { }
#        decimal_places = self._meta.get_field('value').decimal_places
#        self.set_foreign_keys(self)
#        for (field,value) in label_row.items():                
#            # The value field is not transformed
#            if field == 'value':
#                # Make sure to round a potential float to a decimal with 
#                # model/field appropriate decimal places
#                # OBS: This might be unsafe, as the Decimal object might 
#                #      still have precision exceeding the Django table 
#                #      precision. Look for better method!
#                id_row['value'] = round(Decimal(value),decimal_places)
#            # If there is an id (the own id) field it is not transformed
#            elif field in ['id','replaces_id','version_first', 'version_last']:
#                id_row[field] = value
#            elif not field in self.fields:
#                raise ValueError("Field name " + field + " is not a field in " + self.__name__)
#            elif self.field_types[field] == "ForeignKey": 
#                id_row[field+"_id"] = self.foreign_ids[field][value]
#                try:
#                    pass
#                except: 
#                    raise ValueError("Unknown label " + value + "cannot be converted to item_id")
#            else:
#                raise ValueError("Data table field was neither ForeignKey or named 'value'")
#        return id_row


    class Meta:
        abstract = True

