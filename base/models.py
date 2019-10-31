from django.db import models
from decimal import Decimal

from . version import Version
from . errors import NoFieldError, NotDecimalError, NoItemError

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


    def commit(self, version: object) -> None:
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


    def set_fk_labels_objects(self):
        """Set lookup dict for foreign key objects by column name and label."""
        # TODO: Refactor keys.py to use this method
        fc = { 'version_first__isnull': False, 'version_last__isnull': True }
        self.fk_labels_objects = {}
        fields = self.index_fields.copy()
        # We need to be able to look up value_field in mappings_model
        if self.model_type == 'mappings_model':
            fields.append(self.value_field)
        for field in fields:
            self.fk_labels_objects[field] = {}
            column_model = self._meta.get_field(field).remote_field.model
            for item in column_model.objects.filter(**fc):
                self.fk_labels_objects[field][item.label] = item

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
        try:
            return getattr(self,self.value_field)
        # This exception requires malformed user model
        except: # pragma: no cover
            return getattr(self,self.value_field)


    def set_from_cell(self, key, header, value, column_field) -> None:
        """Populate record using cell information.
        
            Arguments:
                key: dict of index_field names(str): index_field labels(str)
                header: label(str) from table header
                value: cell value (str)
                column_field: index label(str) or value_field name(str)
        """
        # A one-column table will have value_field as the single value_header
        # and the value_field name will be identical to the table header
        if column_field == self.value_field and column_field == header:
            record_dict = key.copy()
            record_dict[self.value_field] = value
            self.set_from_record_dict(record_dict)
        # A multi-column table will have an index_field as column field 
        # and the header will be a label from that index_field
        elif column_field in self.index_fields:
            if header in self.fk_labels_objects[column_field].keys():
                record_dict = key.copy()
                record_dict[column_field] = header
                record_dict[self.value_field] = value
                self.set_from_record_dict(record_dict)
            else:
                model = self._meta.get_field(column_field).remote_field.model
                raise NoFieldError(header,model)
        elif header != self.value_field:
            raise NoFieldError(header,self)            
        else: 
            raise NoFieldError(column_field,self)
            
    def set_from_record_dict(self, record_dict: dict) -> None:
        """Populate record using record dict; then validate."""
        # Check that record_dict does not contain other than model fields
        for field in record_dict.keys():
            if field == self.value_field:
                # set_value may raise exception for bad value type
                self.set_value(record_dict[self.value_field])
            else:
                if field not in self.index_fields:
                    raise NoFieldError(field,self)
        # Check that record_dict contains all model fields
        if self.value_field not in record_dict.keys():
            raise NoFieldError(self.value_field, self)
        for index_field in self.index_fields:
            if index_field not in record_dict.keys():
                raise NoFieldError(index_field, self)
            else:
                # Set data_model object using record_dict information
                fk_label = record_dict[index_field]
                try:
                    fk_object = self.fk_labels_objects[index_field][fk_label]
                except:
                    fk_model = self._meta.get_field(index_field).remote_field.model
                    raise NoItemError(fk_label, fk_model)
                else:
                    setattr(self,index_field,fk_object)

    class Meta:
        abstract = True


class DataModel(AssessModel):
    """Abstract class for all our data tables containing value data"""

    model_type = 'data_model'
    fk_label_to_object = {}
            
    def set_value(self, decimal_str: str) -> None:
        """Convert a value string to decimal and set model value_field."""
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        if isinstance(decimal_str, str):
            decimal_str = decimal_str.replace(delimiters['thousands'],'')
            decimal_str = decimal_str.replace(delimiters['decimal'],'.')
        try:
            setattr(self, self.value_field, Decimal(decimal_str))
        except:
            raise NotDecimalError(decimal_str, self)
        

    class Meta:
        abstract = True


class MappingsModel(DataModel):
    """Abstract class for all our mapping tables containing foreign keys."""

    model_type = 'mappings_model'    
    fk_label_objects = {}
            
    def set_value(self, fk_label: str) -> None:
        """Convert value label string to fk object; set model value_field."""
        fk_object = None
        try:
            fk_object = self.fk_labels_objects[self.value_field][fk_label]
        except:
            NoItemError(fk_label, self)
        if fk_object == None:
            raise NoItemError(fk_label, self)
        else:
            setattr(self, self.value_field, fk_object)
    
        
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

    class Meta:
        abstract = True


### Models in base for testing only purposes - do not delete, test.py depends!
 
class TestItemA(ItemModel):
    fields = ['label']
    model_name = 'TestItemA'
    
class TestItemB(ItemModel):
    fields = ['label']
    model_name = 'TestItemB'
    
class TestItemC(ItemModel):
    fields = ['label']
    model_name = 'TestItemC'
    
class TestData(DataModel):
    
    index_fields = ['testitema','testitemb','testitemc']
    column_field = 'testitemc'
    value_field = 'value'
    model_name = 'TestData'
    app_name = 'choices'
    
    testitema = models.ForeignKey(TestItemA,   on_delete=models.CASCADE)
    testitemb = models.ForeignKey(TestItemB,   on_delete=models.CASCADE)
    testitemc = models.ForeignKey(TestItemC,   on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=5, decimal_places=3)

class TestMappings(MappingsModel):
    
    index_fields = ['testitema','testitemb']
    column_field = 'testitemb'
    value_field = 'testitemc'
    model_name = 'TestMappings'
    app_name = 'choices'
    
    testitema = models.ForeignKey(TestItemA,   on_delete=models.CASCADE)
    testitemb = models.ForeignKey(TestItemB,   on_delete=models.CASCADE)
    testitemc = models.ForeignKey(TestItemC,   on_delete=models.CASCADE)
