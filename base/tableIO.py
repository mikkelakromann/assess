from . keys import Keys


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

    def __init__(self,model: object) -> None:
        """Process user supplied input data table into records."""

        self.model = model              # The data_model to be matched

        # An IO datatable column is either a index or value column
        # depending whether the cell context is an index item or a value
        self.model_index_headers = []   # Index headers from DB model
        self.model_value_headers = []   # Value headers from DB model
        self.table_index_headers = []   # Index headers from table
        self.table_value_headers = []   # Value headers from table
        self.table_one_column = True    # Is the table one-column value?
        self.column_field = ""          # Column field (to be calculated later)
        self.value_field = model.value_field

        self.rows = []                  # Rows is a list of header/value dicts
        self.keys = Keys(model)         # Model key lookup for the record dict
        self.records = {}               # The table as dict (key/model_object)



    def set_column_field(self, column_field="") -> None:
        """Set the column field name according to user or model default"""

        # Sanity check of user supplied column_field
        model_fields = self.model.index_fields.copy()
        model_fields.append(self.model.value_field)
        if column_field not in model_fields:
            column_field = ""

        # Set user supplied or model default column_field
        if column_field != "":
            self.column_field = column_field
        else:
            self.column_field = self.model.column_field

        # Calculate the model's and the IO table's headers from column_field
        # If our input table has a column_field which is a database index field
        # there will not be a column with that field name in our input table
        f = self.model.index_fields
        for index_field in self.model.index_fields:
            if index_field != self.column_field:
                self.model_index_headers.append(index_field)
            else:
            # A multi-value_column table has column_field's items
                item_labels = self.keys.indices_labels[index_field]
                self.model_value_headers = item_labels
                self.table_one_column = False

        # A one-value_column table has [value_field] as column_items
        if self.column_field == self.model.value_field:
            self.model_value_headers = list(self.model.value_field)
            self.table_one_column = True


    def parse_excel(self):
        """Parse an excel table into rows (a list of header/value dicts)."""
        # Await later implementation
        pass


    def parse_csv(self, request: object, delimiters: dict) -> dict:
        """Parses CSV string into rows (a list of header/value dicts)."""

        csv_string = request.POST['csv_string']
        column_field = request.POST['column_field']
        self.set_column_field(column_field)

        lines = csv_string.splitlines()
        csv_header = lines.pop(0)

        # Split table fields into index fields and value fields
        table_field_names = csv_header.split(delimiters['sep'])
        table_column_count = len(table_field_names)
        for field in table_field_names:
            if field in self.model_index_headers:
                self.table_index_headers.append(field)
            else:
                self.table_value_headers.append(field)

        # Parse CSV data lines into rows (dict of field_name/value)
        for line in lines:
            cells = line.split(delimiters['sep'])
            if len(cells) == table_column_count:
                row_dict = dict(zip(table_field_names,cells))
                if self.model.model_type == "data_model":
                    for field in self.table_value_headers:
                        row_dict[field].replace(delimiters['thousands'],'')
                        row_dict[field].replace(delimiters['decimal'],'.')
                self.rows.append(row_dict)
            else:
                self.errors.append("CSV line cell count did not match header.")

        self.check_field_names()
        self.parse_rows()
        return self.records


    def check_field_names(self):
        """Check the table headers against the database headers."""

        # Database and table index fields need to be identical sets
        # (we have already sorted the column_field name out of index_fields)
        if set(self.model_index_headers) != set(self.table_index_headers):
            return "Model index fields mismatch against user input index fields."

        # For one-value_column tables, table_value_field == model_value_field
        if self.table_one_column:
            if self.table_value_headers != self.model_value_headers:
                return "The user input value header does not match the model."
        # For multi-value_column tables, table_value_headers must be subsets
        # of the column_field items
        else:
            if not set(self.table_value_headers).issubset(set(self.model_value_headers)):
                return "The user input value headers do not match the items."


    def parse_rows(self):
        """Convert rows (list of list) into records (dict of keys/objects)."""

        for row in self.rows:
            # Create a index key and a dict common to all cells in the CSV line
            index_keys = {}
            index_dict = {}

            value_field = self.value_field
            column_field = self.column_field

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
                    if self.table_one_column:
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
                    value_id = self.keys.get_id(field,cell)
                    if self.table_one_column:
                        record_dict[value_field + "_id"] = value_id
                    else:
                        index_field_name = self.column_field + "_id"
                        index_item_id = self.keys.get_id(field,cell)
                        record_dict[index_field_name] = index_item_id
                        record_dict[value_field + "_id"] = value_id

                record = self.model(**record_dict)
                key = record.get_key()
                # Only add changed records to self.records_changed
                self.records[key] = record


