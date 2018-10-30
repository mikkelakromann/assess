from django.utils.html import escape

class csv_to_list_of_dicts():
    """Splits a CSV formatted string with headers and multiple lines into rows and cells.
    Provides methods for extensive checking that 
    - the CSV headers equals the field names of the model
    - a CSV line has the data content appropriate for the field
    - escaping of malicious strings
    """

    def __init__(self,csv_string,model,delimiters):
        """Executes the steps: (1) header validation, (2) get foreign keys, (3) line parsing"""
        self.lines = csv_string.splitlines()
        self.headers = self.lines.pop(0).split("\t")
        self.model = model
        self.model_name = self.model._meta.object_name.lower()
        self.rows = [ ]
        self.errors = [ ]
        self.fields = model.fields
        self.num_columns = len(model.fields)
        self.field_types = model.get_field_types(model)

        self.validate_headers()
        self.get_foreign_keys()
        self.parse_lines()

    def validate_headers(self):
        """Validate the headers from CSV table against the model's fields both ways""" 
        # Check that all table fields are in the CSV header
        notInHeaders = [ ]
        for field in self.fields:
            if not field in self.headers:
                notInHeaders.append(field)
        # Check that all CSV heades are in the table fields
        notInFields = [ ]
        for header in self.headers:
            if not header in self.fields:
                notInFields.append(header)
        # Set error message to user if there are mismatchs between CSV headers and table fields
        if len(notInFields) != 0 and len(notInHeaders) != 0:     
            raise ValueError("Table fields not in CSV headers: " + ", ".join(notInHeaders) + "; " +
                             "CSV headers not in table fields: " + ", ".join(notInFields))
        elif len(notInFields) != 0:
            raise ValueError("CSV headers not in table fields: " + ", ".join(notInFields))
        elif len(notInHeaders) != 0:
            raise ValueError("Table fields not in CSV headers:" + ", ".join(notInHeaders))
        
    
    def get_foreign_keys(self):
        """Load foreignkeys from foreign models for all fields defined as foreign keys.
        Return error message (string) and field name of id/label (dict)"""
        for field in self.fields:
            if self.field_types[field] == "ForeignKey":
                try:
                    foreign_model = apps.get_model('items',field)
                    self.foreign_keys[field] = foreign_model.get_id_labels_dict(foreign_model)
                except:
                    raise ValueError("Error in retrieving foreign keys. Please check label spelling " + 
                                     "of foreign key fields in models.py: " +  str(self.foreign_keys[field]))
        

    def parse_lines(self):
        """Parse all data lines into the self.rows dict, and add any errors to the error dict
        Splits a CSV line (string) into cells and checks that the cell conforms to the Model's field
        Returns a field dict of values for the row, and a field dict of error messages if any cell did not conform."""
        for line in self.lines:
            cells = line.split("\t")
            row = { }
            error = { }
            for i in range(0, len(cells)):
                field = self.headers[i]
                field_type = self.field_types[field]
# Make sure all relavant text field types are represented here
                if field_type in [ 'ForeignKey' ]:
                    try:
                        row[field + "_id" ] = self.foreign_keys[field][cells[i].strip()]
                    except: 
                        row[field] = "Not a foreign key in " + field + ": "+ cells[i] + "; "
                        error[field] = row[field]
                elif field_type in [ 'CharField' ]:
                    row[field] = escape(cells[i])
# Make sure all relavant real number field types are represented here
                elif field_type in [ 'DecimalField', 'FloatField' ]:
                    try:
                        row[field] = float(cells[i])
                    except:
                        row[field] = "Not real: " + cells[i]
                        error[field] = row[field]
# Make sure all relavant integer number field types are represented here
                elif field_type in [ 'IntegerField' ]:
                    try:
                        row[field] = int(float(cells[i]))
                    except: 
                        row[field] = "Not integer:" + cells[i]
                        error[field] = row[field]
                else:
                    row[field] = "Unknown field type"
                    error[field] = row[field]
                self.rows.append(row)
                self.errors.append(error)

        print(self.errors)
#        if "; ".join(self.errors) != "":
#            raise ValueError("There were errors in parsing the CSV string data lines.")
