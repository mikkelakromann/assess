from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from . keys import Keys
from . history import History
from . version import Version
from . errors import NotCleanRecord, NoRecordIntegrity
from . messages import Messages
from . tableIO import AssessTableIO


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
        self.message = Messages()
        # Records are kept in a dict with values of model objects
        # The record dict keys are tuples of the index fields
        self.records = {}                       # Dict of model objects
        self.records_changed = {}               # Dict of changed model objects
        # Each row is a dict with keys from self.header and values from DB
        self.errors = []                        # List of errors from parsing
        self.rows = []                          # List of row dicts

    def get_context(self):
        """Get context for printing table, history and navigation links."""
        context = {}
        context['table_model_name'] = self.model_name
        if not self.rows == []:
            context['model_type'] = self.model.model_type
            context['value_dict'] = self.keys.value_labels_ids
            context['row_list'] = self.rows
            context['header_list'] = self.keys.index_headers + self.keys.value_headers
            context['header_list_index'] = self.keys.index_headers
            context['header_list_items'] = self.keys.value_headers
            history = History(self.model)
            context['history'] = history.context_data
            context['version_link_id'] = self.version.link_id
        return context

    def render_table_context(self, column_field: str, dif: bool, order=[]) -> dict:
        """Render table to Django template."""
        self.load(dif, order)
        self.set_rows(column_field, 'display')
        context = self.get_context()
        return context

    def set_rows(self,column_field: str, table_type='display') -> None:
        """Pivot table and populate self.rows with table for Django template"""
        # Calculate the table's column headers and row keys
        self.keys = Keys(self.model)
        self.keys.set_headers(column_field)
        # OBS: Perhaps implement ordering of index columns at some point
        # (or rely on jQuery functionality if implemented?)
        key_list = self.keys.get_key_list()
        # keys.get_key_list(): List of tuples - [(item1,itemX),(item2,itemX)]
        for key in key_list:
            # The row is a dict of header names and cell values for that row
            # Add index_headers and index values (from key) to the row
            row = dict(zip(self.keys.index_headers,key))
            # Add value cells to row by looking up the value in self.records
            for value_header in self.keys.value_headers:
                # The record key also contains the value_header key, and its
                # index_fields are always sorted by self.model.index_fields
                record_key = ()
                for index_field in self.model.index_fields:
                    if index_field == self.keys.column_field:
                        record_key += (value_header,)
                    elif index_field in self.keys.index_headers:
                        record_key += (row[index_field],)
                # data_model: the value index field is value_field for all rows
                record_key += (self.model.value_field,)
                # Try to pick the record value from the loaded DB records
                try:
                    record = self.records[record_key]
                # Do nothing (no value) if the key's record does not exist
                except:
                    row[value_header] = 'n.d.'
                # Assign value to the cell in the table row to be displayed
                else:
                    row[value_header] = str(record.get_value())
                    row[value_header + '_id'] = record.id
                    row[value_header + '_key'] = str(record.get_key())
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
        # Create record dict with key being tuple of index fields and
        # values being model objects
        # If records are sorted from lowest to highest id, the record
        # dict will end up having only the one latest record for all versions
        self.records = {}
        for model_object in query:
            key = model_object.get_key()
            self.records[key] = model_object

    def save_POST(self, POST: dict) -> None:
        """Parse a POST dict from edit_view and save changes to DB."""
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        tableIO = AssessTableIO(self.model, delimiters)
        records = tableIO.parse_POST(POST)
        self.errors = tableIO.errors
        # Load current records, so that we can save only changed records
        self.load(False)
        self.save_changed_records(records)

    def save_CSV(self, POST: dict) -> None:
        """Parse CSV table data from upload_view and save changes to DB."""
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        tableIO = AssessTableIO(self.model, delimiters)
        records = tableIO.parse_csv(POST)
        self.errors = tableIO.errors
        # Load current records, so that we can save only changed records
        self.load(False)
        self.save_changed_records(records)

    def get_CSV_form_context(self) -> dict:
        """Return context for table upload form."""
        context = {}
        col_list = []
        # The upload form need a HTML select input for selecting column field
        for column in self.model.index_fields + [self.model.value_field]:
            col_dict = {}
            col_dict['label'] = column
            col_dict['name'] = column.capitalize()
            # Default for the select input is the model column field
            if column == self.model.column_field:
                col_dict['checked'] = ' checked'
            col_list.append(col_dict)
        context['column_field_choices'] = col_list
        context['model_name'] = self.model_name
        return context

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
                    old_record_value = Decimal(old_record.get_value())
                    new_record_value = Decimal(new_record.get_value())
                # other models has foreignkey value
                else:
                    old_record_value = old_record.get_value()
                    new_record_value = new_record.get_value()
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
                    else:
                        record.save()
            # Integrity errors are caused by unique constraints and ??
            except IntegrityError as error:
                raise NoRecordIntegrity(record,error)

    def get_commit_form_context(self) -> dict:
        """Return context for the table_commit form."""
        k = { 'model_name': self.model_name }
        context = k.copy()
        context['table_commit_heading'] = self.message.get('table_commit_heading',k)
        context['table_commit_notice'] = self.message.get('table_commit_notice',k)
        context['table_commit_submit'] = self.message.get('table_commit_submit',k)
        context['table_commit_reject'] = self.message.get('table_commit_reject',k)
        context['i18n_user'] = self.message.get('i18n_user',k)
        context['i18n_label'] = self.message.get('i18n_label',k)
        context['i18n_note'] = self.message.get('i18n_note',k)
        context['table_commit_notable'] = self.message.get('table_commit_notice',k)
        return context


    def commit_rows(self,version_info: dict) -> None:
        """"Add new DB version, commit DB records version_first=version_id."""
        version_info_clean = {}
        for key in version_info.keys():
            if key in ['label','user','note']:
                version_info_clean[key] = version_info[key]
        # Add a new version to the Version table
        version = Version.objects.create(**version_info_clean)
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

