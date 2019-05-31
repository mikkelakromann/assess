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


    def commit(self,version: object) -> None:
        """Commit record and set replaced record to archived."""

        # Set a filter for all current record with same index as this record
        fi = version.kwargs_filter_current()
        for field in self.index_fields:
            fi[field] = getattr(self,field)

        # Archive the identified currect record(s) (version_last = version.id)
        for archived in self.__class__.objects.filter(**fi):
            archived.version_last = version
            archived.save()

        # Set this record to current by setting its version_first to version.id
        self.version_first = version
        self.save()


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


    def get_label(self,item_id):
        """Return item label name"""

        # NEED ERROR CHECKING HERE???
        item = self.objects.get(pk=item_id)
        return item.label


    def delete(self,item_id):
        """Delete the item by setting version status to archived for item and its keys"""

        delete_label = self.objects.get(pk=item_id).label
        l = "Deleted label " + delete_label + " in " + self.__name__
        v = Version.objects.create(label=l, model_name=self.__name__)
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
            v = Version.objects.create(label=l, model_name=self.__name__)
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
    """Abstract class for all our data tables containing value data"""

    model_type = 'data_model'

    # Consider moving this definition inside collection.py, only place its used
    # OBS: Now also used in tableIO.py ... perhaps smart choice, since we can
    #      then change key everywhere in one go
    def get_key(self):
        """Return record key (tuple of the record's index fields's values)"""
        keys = []
        for field in self.index_fields:
            keys.append(str(getattr(self,field)))
        keys.append(self.value_field)
        return tuple(keys)


    class Meta:
        abstract = True


class MappingsModel(DataModel):
    """Abstract class for all our mapping tables containing foreign keys."""

    model_type = 'mappings_model'    
    
    class Meta:
        abstract = True
