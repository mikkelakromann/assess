import pandas
from . keys import Keys
from . errors import AssessError, CSVheaderMalformed, CSVwrongColumnCount, \
                     CSVfieldNotFound


class AssessTableIO():
    """Class for parsing user supplied input tables."""
        # data_model and mapping_model can take two forms as input table:
        # - All index fields are columns, and one column is value_field
        # - All but one index field are columns, the last field is a column
        #   field, so values for each item in column field has a data column
        # In data_model, the value field is a Decimal
        # In mappings_model, the value field is a ForeignKey
        # Each CSV value cell corresponds to a model object
        # We temporarily construct an object for each cell, done in 3 steps:
        #  1) Calculate index_key of the object from the index_field
        #  2) Add the column_field item if we have such one
        #  3) Calculate the value_field (data_model or mappings_model)
        #  4) Add the object from index_key and value if value differs
        #     from the value in the existing record
        # If it's value is different from the database value (in self.records)
        # the object is stored in self.changed_records for later processing
        # OBS: We could have used DataFrames for processing, but we then would
        #      miss extensive error checking and detailed error reporting

    def __init__(self,model: object, delimiters: dict) -> None:
        """Process user supplied input data table into records."""
        self.model = model              # The data_model to be matched
        self.delimiters = delimiters    # Delimiters, user's or default
        # An IO datatable column is either a index or value column
        # depending whether the cell context is an index item or a value
        self.table_index_headers = []   # Index headers from table
        self.table_value_headers = []   # Value headers from table
        self.rows = []                  # Rows is a list of header/value dicts
        self.keys = Keys(model)         # Model key lookup for the record dict
        self.records = {}               # The table as dict (key/model_object)
        self.errors = []                # List of exceptions reporting errors


    def parse_POST(self, POST: dict) -> dict:
        """Parse POST'ed edit form, errorcheck and return as key/record dict"""
        # parse_POST is a single step, as each POST key/value pair
        # contains all information about both record key and record value
        # In the POST dict we expect record_id/value_id key/value pairs
        # for mapping_model and record_id/decimal for data_model
        for key_str,value_str in POST.items():
            record = self.model()
            record.fk_labels_objects = self.keys.indices_labels_objects
            # Make the key part of POST into a record key
            try:
                # keys.split:key_str returns key tuple and field_name/id dict
                key,record_dict = self.keys.split_key_str(key_str)
            # Keys.split_key_str may raise KeyNotFound or KeyInvalid
            except AssessError as e:
                self.errors.append(e)
            else:
                record_dict[self.model.value_field] = value_str
                try:
                    record.set_from_record_dict(record_dict)
                except AssessError as e:
                    self.errors.append(e)
                else:
                    self.records[key] = record
        return self.records

    def get_dataframe(self, version: object) -> object:
        """Returns pandas dataframe for current version of table."""
        # We want current version of the table
        # TODO: Answer Why?
        # TODO: AppIO expects to get the version of the object argument
        #       but we force current - fix?
        cur_fil = version.kwargs_filter_current()
        # Get list of record values for index fields, we want label, not id
        val_lst = []
        for field in self.model.index_fields:
            val_lst.append(field + '__label')
        # We want the value field fk label for mappings_models
        if self.model.model_type == 'mappings_model':
            val_lst.append(self.model.value_field + '__label')
        # and the value_field string for data_model
        else:
            val_lst.append(self.model.value_field)
        query = self.model.objects.filter(**cur_fil).values(*val_lst)
        df_unordered = pandas.DataFrame.from_records(query)
        # Ensure that dataframe column order is right for e.g. Excel generation
        # Remove the __label from the dataframe column names
        if not df_unordered.empty:
            # Ensure that dataframe column order is right for Excel generation
            df = df_unordered[val_lst]
            # Remove the __label from the dataframe column names
            column_names = self.model.index_fields.copy()
            column_names.append(self.model.value_field)
            df.columns = column_names
            return df
        else:
            return pandas.DataFrame()

    def parse_dataframe(self, dataframe) -> dict:
        # TODO: Do validation of field using DataModel and MappingsModel func.
        """Parse dataframe and return dict of record objects."""
        self.keys.set_headers(self.model.value_field)
        self.table_index_headers = self.keys.index_headers
        self.table_value_headers = self.keys.value_headers
        # TODO: Add check that dataframe column names match model fields
        for record_dict in dataframe.to_dict('records'):
            record = self.model()
            record.fk_labels_objects = self.keys.indices_labels_objects
            try:
                record.set_from_record_dict(record_dict)
            except AssessError as e:
                self.errors.append(e)
            else:
                key = record.get_key()
                self.records[key] = record
        return self.records

    def parse_csv(self, POST: dict) -> dict:
        """Parses CSV string, errorcheck and return as key/record dict"""
        # TODO: Add try/exception
        csv_string = POST['csv_string']
        column_field = POST['column_field']
        # keys.set_headers() will not fail but default to model.column_field
        # if an invalid column_field is supplied by POST
        self.keys.set_headers(column_field)
        lines = csv_string.splitlines()
        csv_header = lines.pop(0)
        # Split table fields into index fields and value fields
        csv_headers = csv_header.split(self.delimiters['sep'])
        csv_column_count = len(csv_headers)
        table_headers = self.keys.index_headers + self.keys.value_headers
        # check_table_headers may raise NoFieldError - transform to a CSV error
        try: 
            (ti, tv) = self.keys.split_table_headers(csv_headers)
        except AssessError as e1:
            msg = str(e1)
            e2 = CSVheaderMalformed(csv_headers, table_headers, msg, self.model)
            self.errors.append(e2)
            return {}
        self.table_index_headers = ti
        self.table_value_headers = tv
        for line in lines:
            cells = line.split(self.delimiters['sep'])
            if len(cells) != csv_column_count:
                e = CSVwrongColumnCount(cells,csv_headers,'',self.model)
                self.errors.append(e)
            else:
                row_dict = dict(zip(csv_headers,cells))
                key_dict = {}
                for field in self.table_index_headers:
                    # Try/except not necessary, since field is always a key of
                    # row_dict, as this is zipped from csv_headers
                    key_dict[field] = row_dict[field]
                for header in self.table_value_headers:
                    record = self.model()
                    record.fk_labels_objects = self.keys.indices_labels_objects
                    # Try/except not necessary, since header is always a key of
                    # row_dict, as this is zipped from csv_headers
                    cell = row_dict[header]
                    try:
                        # set_from_cell() may raise NoFieldError
                        record.set_from_cell(key_dict, header, cell, column_field)
                    except AssessError as e1:
                        msg = str(e1)
                        CSVrow = list(row_dict.values())
                        e2 = CSVfieldNotFound(CSVrow, table_headers, msg, self.model)
                        self.errors.append(e2)
                    else:
                        key = record.get_key()
                        self.records[key] = record
        if self.errors == []:
            return self.records
        else:
            return {}
