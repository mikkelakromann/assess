class Keys():
    """Provide row keys, table headers and column item label/ud lookup dicts"""

    def __init__(self,model):

        self.model = model
        foreignkey_columns = model.index_fields.copy()
        # Mappings model values are foreign keys, must be added to key lookup
        if self.model.model_type == 'mappings_model':
            foreignkey_columns.append(self.model.value_field)

        # Headers are for reading/displaying tables in other pivoting 
        self.headers = []                       # List of header strings
        # The union of item_headers and index_headers is equal to headers
        self.value_headers = []                 # List of value header strings
        self.index_headers = []                 # List of index header strings
        # Is table 1-column (value_field) or multi-column (column_field items)
        self.table_one_column = False           

        # Lookup dicts for index field names and item ids and item labels
        self.indices_ids_labels = {}    # Dict of dicts {field: {id: label}, }
        self.indices_labels_ids = {}    # Dict of dicts {field: {label: id}, }
        self.indices_labels = {}        # Dict of lists {field: [label, ]}
        # OBS: Trying to return the indices items for specified archied
        # versions is going to be really messy. Current items are needed for
        # chekcing of user upload data integrity
        dimensions = []
        self.size = 1
        for column_name in foreignkey_columns:
            try:
                # Get the foreign key model items for each index in collection
                column_model = self.model._meta.get_field(column_name).remote_field.model
            except:
                # Bad stuff will happen when self.index_field supplied in
                # app_name / models.py does not reflect the model's columns
                # ### OBS: Provide better error message from messages.py
                return column_name + "internal error."
            ids_labels = {}
            labels_ids = {}
            labels = []
            # Preferably the version filters should be imported from version.py
            # but this depend on keys so we cant.
            fc = { 'version_first__isnull': False, 'version_last__isnull': True }
            for item in column_model.objects.filter(**fc):
                ids_labels[item.id] = item.label
                labels_ids[item.label] = item.id
                labels.append(item.label)

            # Count dimension of the different indices
            s = len(labels)
            self.size = self.size*s
            dimensions.append(str(s))
            # Store the list and dicts in the collection object
            self.indices_ids_labels[column_name] = ids_labels
            self.indices_labels_ids[column_name] = labels_ids
            self.indices_labels[column_name] = labels

        # Text string for description of table dimension
        self.dimension = "{" + " x ".join(dimensions) + "}"


    def set_headers(self, column_field="") -> None:
        """Calculate headers according to user choice of column field."""

        # Sanity check of user supplied column_field
        # Use model default column_field if necessary
        model_fields = self.model.index_fields.copy()
        model_fields.append(self.model.value_field)
        if column_field in model_fields:
            self.column_field = column_field
        else:
            self.column_field = self.model.column_field

        # Calculate the model's and the table's headers from column_field
        # If our table has a column_field which is a database index field
        # there will not be a column with that field name in our input table
        for index_field in self.model.index_fields:
            if index_field != self.column_field:
                self.index_headers.append(index_field)
            else:
            # A multi-value_column table has column_field's items
                item_labels = self.indices_labels[index_field]
                self.value_headers = item_labels
                self.table_one_column = False

        # If one-value_column table, the only value header is value_field
        if self.column_field == self.model.value_field:
            self.table_one_column = True
            self.value_headers.append(self.model.value_field)
        # In mapping_model: If value_field isn't the column, then it's an index 
        elif self.model.model_type == 'mappings_model':
            self.index_headers.append(self.model.value_field)


    def get_key_list(self):
        """Return list of keys (key is a tuple of item labels) """

        # OBS: Implement ordering of indices at some point
        order = self.index_headers
        indices = {}
        for field in order:
            indices[field] = self.indices_labels[field]
        # combos: dict of list of all combinations of items by column name
        # { col1_name: [item1,item2, ...], col2_name: [itemX,itemX, ...]}
        key_combos = self.item_combos(order,indices,{})
        # key list of tuples: [(item1,itemX), (item2,itemX), (item1,itemY), ..]
        return list(zip(*key_combos.values()))


    def item_combos(self,__order,__indices,__columns):
        """Recursively span out all combination of indices to key dicts

            Arguments:
                order: list of str field names for ordering of the columns
                indices: dict of list of items still to be arranged in columns
                columns: dict of list of itmes already arranged in columns
        """

        # indices1 = {c1: [iX,iY]}
        # indices2 = {c2: [iA,iB]}
        # keys3 = {c3: [i1,i2,i3]}
        # indices12 = {c1: [iX,iY], c2: [iA,iB] }
        # indices123 = {c1: [iX,iY], c2: [iA,iB], c3: [i1,i2,i3] }
        # F(indices123,[]) = F(indices12,keys3)
        # F(indices12,keys3) F(indices1,F(indices2,keys3))
        # F(indices2,keys3) = keys23
        # keys23 = {c2: [iA,iA,iA,iB,iB,iB], c3: [i1,i2,i3,i1,i2,i3]}

        # The routine rearranges the inputs - make copies
        order = __order.copy()
        indices = __indices.copy()
        columns = __columns.copy()


        # Arrange to columns if there are more indices
        if len(indices) > 0:
            # Calculate the number of rows in already arranged columns
            if len(columns) > 0:
                # We must have a field name to select a dict item, use first
                first_field_name = list(columns.keys())[0]
                column_length = len(columns[first_field_name])
            else:
                column_length = 1
            # Find next field to arrange, and get its items for a new column
            field = order.pop()
            items = indices.pop(field)
            new_columns = { field: [] }
            # In the new column, the items are repeated with the length of
            # the already arranged columns
            for i in items:
                new_columns[field].extend([i]*column_length)
            # The already arranged columns are duplicated with the number
            # of items in the new column
            for column_name in columns.keys():
                new_columns[column_name] = columns[column_name]*len(items)
            # Recursively call back
            return self.item_combos(order,indices,new_columns)
        # If no more indices, we're done doing the arranged columns
        else:
            return columns


