from django.db import models

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


    # Consider moving this definition inside collection.py, only place its used
    # OBS: Now also used in tableIO.py ... perhaps smart choice, since we can
    #      then change key everywhere in one go
    def get_key(self):
        """Return record key (tuple of the record's index fields's values)"""
        keys = []
        for field in self.index_fields:
            value = str(getattr(self,field))
            keys.append(value)
        keys.append(self.value_field)
        return tuple(keys)
    
    
    # TODO: Perhaps move to data_model and mappings_model and return as 
    # Decimal object or Item object
    # Additionally perhaps also deliver common method for return as string
    # modified each of the two models
    def get_value(self):
        """Return the value field of the model."""
        if self.value_field != "":
            return getattr(self,self.value_field)
        else:
            return None


    class Meta:
        abstract = True


class DataModel(AssessModel):
    """Abstract class for all our data tables containing value data"""

    model_type = 'data_model'


    class Meta:
        abstract = True


class MappingsModel(DataModel):
    """Abstract class for all our mapping tables containing foreign keys."""

    model_type = 'mappings_model'    
    
        
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


    class Meta:
        abstract = True


### Models in base for testing only purposes - do not delete, test.py depends!
 
class TestItemA(ItemModel):
    fields = ['label']
    
class TestItemB(ItemModel):
    fields = ['label']
    
class TestItemC(ItemModel):
    fields = ['label']
    
class TestData(DataModel):
    
    index_fields = ['testitema','testitemb','testitemc']
    column_field = 'testitemc'
    value_field = 'value'
    model_name = 'testdata'
    app_name = 'choices'
    
    testitema = models.ForeignKey(TestItemA,   on_delete=models.CASCADE)
    testitemb = models.ForeignKey(TestItemB,   on_delete=models.CASCADE)
    testitemc = models.ForeignKey(TestItemC,   on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=5, decimal_places=3)

class TestMappings(MappingsModel):
    
    index_fields = ['testitema','testitemb']
    column_field = 'testitemb'
    value_field = 'testitemc'
    model_name = 'testmappings'
    app_name = 'choices'
    
    testitema = models.ForeignKey(TestItemA,   on_delete=models.CASCADE)
    testitemb = models.ForeignKey(TestItemB,   on_delete=models.CASCADE)
    testitemc = models.ForeignKey(TestItemC,   on_delete=models.CASCADE)
