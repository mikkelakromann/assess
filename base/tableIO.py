import pandas
from decimal import Decimal
from . keys import Keys
from . errors import AssessError, NoItemError


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

    
    def str2decimal(self,decimal_str) -> Decimal:
        """Convert string to decimal value using Anglo Saxon punctuation."""
        
        # Not implemented conversion to Decimal object yet
        decimal_str.replace(self.delimiters['thousands'],'')
        decimal_str.replace(self.delimiters['decimal'],'.')
        return decimal_str

    
    def parse_excel(self):
        """Parse an excel table into rows (a list of header/value dicts)."""
        # Await later implementation
        pass


    def parse_POST(self, POST: dict) -> dict:
        """Parse POST'ed edit form, errorcheck and return as key/record dict"""
        
        # parse_POST is a single step, as each POST key/value pair
        # contains all information about both record key and record value
        # In the POST dict we expect record_id/value_id key/value pairs 
        # for mapping_model and record_id/decimal for data_model
        for key_str,value_str in POST.items():
            # Make the key part of POST into a record key
            try:
                # keys.split:key_str returns key tuple and field_name/id dict
                key,record_dict = self.keys.split_key_str(key_str)
                
            # Keys.split_key_str may raise KeyNotFound or KeyInvalid
            except AssessError as e:
                self.errors.append(e)
            else:
                # For mappings_model the value is a foreignkey label
                if self.model.model_type == 'mappings_model':
                    try:
                        # We need the value_id for constructing the record
                        value_id = self.keys.value_labels_ids[value_str]
                    except:
                        # and a list of errors where the label wasn't found
                        self.errors.append(NoItemError(value_str,self.model))
                    else:
                        # Add to records ff the key and value is valid
                        record_dict[self.model.value_field + '_id'] = value_id
                        record = self.model(**record_dict)
                        self.records[key] = record
                # For data_model, the value is decimal
                elif self.model.model_type == 'data_model':
                    try:
                        # Convert, also taking into account decimal punctuation
                        value = self.str2decimal(value_str)
                    except AssessError as e:
                        # Add to errors, if value was not decimal
                        self.errors.append(e)
                    else:
                        # Add to records if the key and value is valid
                        record_dict[self.model.value_field] = value 
                        record = self.model(**record_dict)
                        self.records[key] = record
                # Do nothing for model types we dont know
                else:
                    pass
        return self.records


    def get_dataframe(self, version: object) -> object:
        """Returns pandas dataframe for current version of table."""

        # We want current version of the table
        # TODO: Answer Why?
        cur_fil = version.kwargs_filter_current()
        # Get list of record values for index fields, we want label, not id
        val_lst = []
        for field in self.model.index_fields:
            val_lst.append(field + '__label')
        # And we want the value field
        val_lst.append(self.model.value_field)
        query = self.model.objects.filter(**cur_fil).values(*val_lst)
        df = pandas.DataFrame.from_records(query)
        # Remove the __label from the dataframe column names
        if not df.empty:
            column_names = self.model.index_fields
            column_names.append(self.model.value_field)
            df.columns = column_names 
        return df


    def parse_dataframe(self, dataframe) -> dict:
        """Parse dataframe and return dict of record objects."""

        self.keys.set_headers(self.model.value_field)
        self.table_index_headers = self.keys.index_headers
        self.table_value_headers = self.keys.value_headers
        # TODO: Add check that dataframe column names match model fields
        for row in dataframe.to_dict('records'):
            self.rows.append(row)
        self.__parse_rows()
        return self.records


    def parse_csv(self, POST: dict) -> dict:
        """Parses CSV string, errorcheck and return as key/record dict"""
        
        # CSV parsing is split into two parts:
        # 1) Parse the string to a rows consisting of header/value dicts
        # 2) Parse the rows of dicts into records (model objects)

        csv_string = POST['csv_string']
        column_field = POST['column_field']
        self.keys.set_headers(column_field)

        lines = csv_string.splitlines()
        csv_header = lines.pop(0)

        # Split table fields into index fields and value fields
        table_field_names = csv_header.split(self.delimiters['sep'])
        table_column_count = len(table_field_names)
        for field in table_field_names:
            if field in self.keys.index_headers:
                self.table_index_headers.append(field)
            else:
                self.table_value_headers.append(field)

        # Parse CSV data lines into rows (dict of field_name/value)
        for line in lines:
            cells = line.split(self.delimiters['sep'])
            if len(cells) == table_column_count:
                row_dict = dict(zip(table_field_names,cells))
                if self.model.model_type == "data_model":
                    for field in self.table_value_headers:
                        # TODO: replace with self.str2decimal
                        row_dict[field].replace(self.delimiters['thousands'],'')
                        row_dict[field].replace(self.delimiters['decimal'],'.')
                self.rows.append(row_dict)
            else:
                # TODO: Append custom exception instead
                self.errors.append("CSV line cell count did not match header.")

        # Continue checking field names if initial parsing went OK
        if self.errors == []:
            self.__check_field_names()
        else:
            return {}

        # Continue parsing rows if initial parsing went OK
        if self.errors == []:
            self.__parse_rows()
        else:
            return {}

        return self.records


    def __check_field_names(self):
        """Check the table headers against the database headers."""
        # Database and table index fields need to be identical sets
        # (we have already sorted the column_field name out of index_fields)
        if set(self.keys.index_headers) != set(self.table_index_headers):
            # TODO: Append custom exception instead
            e = "Model index fields " + str(self.keys.index_headers) + \
                "mismatch against user input index fields " + \
                str(self.table_index_headers)
            self.errors.append(e)

        # For one-value_column tables, table_value_field == model_value_field
        if self.keys.table_one_column:
            if self.table_value_headers != self.keys.value_headers:
                # TODO: Append custom exception instead
                e = "Model value fields " + str(self.keys.value_headers) + \
                    "mismatch against user input value fields " + \
                    str(self.table_value_headers)
                self.errors.append(e)
            
        # For multi-value_column tables, table_value_headers must be subsets
        # of the column_field items
        else:
            if not set(self.table_value_headers).issubset(set(self.keys.value_headers)):
                # TODO: Append custom exception instead
                e = "Model value fields " + str(self.keys.value_headers) + \
                    "mismatch against user input value fields " + \
                    str(self.table_value_headers)
                self.errors.append(e)


    def __parse_rows(self):
        """Convert rows (list of list) into records (dict of keys/objects)."""

        for row in self.rows:
            # Create a index key and a dict common to all cells in the CSV line
            index_keys = {}
            index_dict = {}

            value_field = self.model.value_field
            column_field = self.keys.column_field

            # Create dicts for index field item keys and ids 
            for field in self.table_index_headers:
                cell = row[field]
                index_keys[field] = cell
                item_id = self.keys.indices_labels_ids[field][cell]
                index_dict[field+"_id"] = item_id

            # Value: Cell is Decimal for data_models and id for mappings_model
            for field in self.table_value_headers:
                record_keys = index_keys.copy()
                record_dict = index_dict.copy()
                cell = row[field]
                record_keys[value_field] = value_field
                # In the data models, the value cells are decimal
                if self.model.model_type == "data_model":
                    if self.keys.table_one_column:
                        # In one-column value tables, use the Decimal value
                        record_dict[value_field] = cell
                    else:
                        # In multi-column value tables, transform column label
                        # to item_id and store also as index key, save cell as Decimal
                        index_item_id = self.keys.indices_labels_ids[column_field][field]
                        index_field_name = column_field + "_id"
                        record_dict[index_field_name] = index_item_id
                        record_dict[value_field] = cell
                        record_keys[column_field] = field
                # In the mappings_model the value field is a foreign key
                elif self.model.model_type == "mappings_model":
                    if self.keys.table_one_column:
                        # With one column, field == value_field
                        value_id = self.keys.indices_labels_ids[field][cell]
                        record_dict[value_field + "_id"] = value_id
                    else:
                        # Multi column: field is a column_field item,
                        # Look up cell item ids with value_field
                        value_id = self.keys.indices_labels_ids[value_field][cell]
                        index_item_id = self.keys.indices_labels_ids[column_field][field]
                        index_field_name = column_field + "_id"
                        record_dict[index_field_name] = index_item_id
                        record_dict[value_field + "_id"] = value_id

                record = self.model(**record_dict)
                key = record.get_key()
                # Only add changed records to self.records_changed
                self.records[key] = record


