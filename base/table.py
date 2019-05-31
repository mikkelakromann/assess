from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from . keys import Keys
from . history import History
from . version import Version
from . errors import NotCleanRecord, NoRecordIntegrity


class AssessTable():
    """Abstract class for collections of AssessModel objects."""

    def __init__(self,model: object, version: str) -> None:
        """Initialise the collection from AssessModel / Django model.

            model (object): Django database object in collection
            version (str): int digit for archived, proposed or current
        """

        self.model = model                      # Model object
        self.model_name = self.model.__name__.lower()
        self.version = Version()
        self.version.set_version_id(version)


        # Collections support tables with one or more index fields, zero or one
        # column fields and exactly one value field
        # Fields are either an index field or the value field
        self.index_fields = model.index_fields  # list: Index field names
        self.value_field = model.value_field    # String: Value field name

        # column_field should be value_field or an element in index_fields
        self.column_field = model.column_field  # String: Column field name

        # Records are kept in a dict with values of model objects
        # The record dict keys are tuples of the index fields
        self.records = {}                       # Dict of model objects
        self.records_changed = {}               # Dict of changed model objects

        # Lists for rendering table in template: headers is for the template
        # These are set by .pivot_1dim()
        self.headers = []                       # List of header strings
        # The union of item_headers and index_headers is equal to headers
        self.item_headers = []                  # List of item header strings
        self.index_headers = []                 # List of index header strings
        # Each row is a dict with keys from self.header and values from DB
        self.rows = []                          # List of row dicts


    def get_context(self):
        """Get context for printing table, history and navigation links."""

        context = {}
        context['table_model_name'] = self.model_name
        if not self.rows == []:
            context['row_list'] = self.rows
            context['header_list'] = self.headers
            context['header_list_index'] = self.index_headers
            context['header_list_items'] = self.item_headers
            history = History(self.model)
            context['history'] = history.context_data
            context['version_name'] = self.version.name
        return context


    def render_table(self, column_field: str, template_name: str) -> object:
        """Render table to Django template."""
        # Consider making a render method to simplify views.py 
        pass


    def set_rows(self,column_field: str) -> None:
        """Pivot table and populate self.rows with table for Django template"""

        keys = Keys(self.model)
        if column_field != "":
            self.column_field = column_field
        indices = {}
        order = []
        for field in self.index_fields:
            if field != self.column_field:
                order.append(field)
                indices[field] = keys.indices_labels[field]

        # Create table for template with pivoted table
        self.headers = order + keys.indices_labels[self.column_field]
        self.index_headers = order
        # Single (value) and multi-column (items) tables differ
        if self.column_field != self.model.value_field:
            # Multi-column has headers from items of column_field
            self.item_headers = keys.indices_labels[self.column_field]
            order.append(self.model.value_field)
        else:
            # Single-column has the value field as header
            self.item_headers.append(self.model.value_field)

        print(self.column_field)
        print(self.value_field)
        print("Order: " + str(order))
        # key_combos: dict of list of all combinations of items by column name
        # { col1_name: [item1,item2, ...], col2_name: [itemX,itemX, ...]}
        key_combos = keys.item_combos(order,indices,{})
        # Create list of keys (tuples): [(item1,itemX),(item2,itemX)]
        key_list = list(zip(*key_combos.values()))

        # OBS: Is this loop better placed in keys.py?
        print("Key list: " + str(key_list))
        row = {}
        for key in key_list:
            # Create index cells from index field names (order) and key values
            row = dict(zip(order,key))
            # Create value cells by iterating over items in column_field
            for column_field in self.item_headers:
                # Create a record key tupple for self.records
                # The order of the key elements must equal self.index_fields
                key = ()
                for index_field in self.index_fields:
                    if index_field in self.column_field:
                        key += (column_field,)
                    else:
                        key += (row[index_field],)
                key += ('value',)
                try:
                    row[column_field] = self.records[key].value
                except:
                    pass
            # When all column_fields are done, the row is done
            self.rows.append(row.copy())



    def load(self, changes: bool ,order=[]) -> None:
        """Load model object fields by version to self.records

        Arguments
            order (list): list of Django field names for .order()
            changes (bool): True for version changes, False for full version
        """

        # Order is the ordering list of fields, if empty use model.index_fields
        if order == []:
            order = self.model.index_fields

        # Execute query according to version and load into data frame
        fv = self.version.kwargs_filter_load(changes)
        query = self.model.objects.filter(**fv).order_by(*order)

        # Create record dict with key being tuple of index fields
        # If records are sorted from lowest to highest id, the record
        # dict will end up having only the one latest record for all versions
        self.records = {}
        for record in query:
            key = record.get_key()
            self.records[key] = record


    def save_changed_records(self,records: dict) -> None:
        """Filter records that were changed, and save them."""

        self.records_changed = {}
        for (key,new_record) in records.items():
            try:
                # We cannot be sure record[key] exist, may be new record
                old_record = self.records[key]
            except:
                # If no old record with key, new record is new: save it
                self.records_changed[key] = new_record
            else:
                # data_model has decimal value, recast to truly compare
                if self.model.model_type == 'data_model':
                    old_record_value = Decimal(old_record.value)
                    new_record_value = Decimal(new_record.value)
                # other models has foreignkey value
                else:
                    old_record_value = old_record.value
                    new_record_value = new_record.value
                # Save only changed values
                if new_record_value != old_record_value:
                    self.records_changed[key] = new_record
        self.save()


    def save(self) -> None:
        """Save proposed records to Django model database table."""

        with transaction.atomic():
            try:
                for (key,record) in self.records_changed.items():
                    try:
                        record.full_clean()
                    # Validation errors are caused by out of spec numerical
                    # and string values, and keys to wrong items
                    except ValidationError as error:
                        raise NotCleanRecord(record,error)
                    record.save()
            # Integrity errors are caused by unique constraints and ??
            except IntegrityError as error:
                raise NoRecordIntegrity(record,error)


    def commit_rows(self,version_info: dict) -> None:
        """"Add new DB version, commit DB records version_first=version_id."""

        # Add a new version to the Version table
        version = Version.objects.create(**version_info)

        # Get metrics information related to proposed changes and save version
        version.set_version_id("proposed")
        version.set_metrics(self.model)
        version.save()

        # Iterate all proposed records and commit them (setting version_first
        # to this version) and set the key identical record to archived
        # (version_last to this version)
        fp = version.kwargs_filter_proposed()
        for record in self.model.objects.filter(**fp):
            record.commit(version)


    def revert_proposed(self) -> None:
        """Delete all proposed rows (with empty version_begin and version_end)."""

        v = Version()
        fp = v.kwargs_filter_proposed()
        self.model.objects.filter(**fp).delete()


    def proposed_count(self) -> int:
        """Return number of proposed rows."""

        v = Version()
        fp = v.kwargs_filter_proposed()
        return self.model.objects.filter(**fp).count()


    class Meta:
        abstract = True
