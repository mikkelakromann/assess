from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.html import escape
from django.apps import apps

class csv_to_django_model:
    """Splits a CSV formatted string with headers and multiple lines into rows and cells.
    Provides methods for extensive checking that 
    - the CSV headers equals the field names of the model
    - a CSV line has the data content appropriate for the field
    - escaping of malicious strings
    """

    def __init__(self,csv_string,model,delimiters):
        self.lines = csv_string.splitlines()
        self.headers = self.lines.pop(0).split("\t")
        self.model = model
        self.model_name = self.model._meta.object_name.lower()
        self.rows = [ ]
        self.errors = [ ]
        self.fields = model.fields
        self.num_columns = len(model.fields)
        self.field_types = model.get_field_types(model)

    def save_to_database(self):
        """Executes the steps: (1) header validation, (2) get foreign keys, (3) line parsing, (4) object saving"""
        error_message = ""
        error_message = self.validate_headers()
        if error_message != "":
            return error_message
        print("passed header validation")
        (error_message,self.foreign_keys) = self.get_foreign_keys()
        if error_message != "":
            return error_message
        print("passed get_foreign_keys")
        error_message = self.parse_lines()
        if error_message != "":
            return error_message
        print("passed parse_lines")
        error_message = self.save_objects()
        if error_message != "":
            return error_message
        print("passed save_objects")
            
    def validate_headers(self):
        """Validate the headers (list) from CSV table against the model's fields (list). 
        Compare the lists two ways.
        Return empty string on successful validation. 
        Return error message on unsuccessful validation."""
        # Check that all table fields are in the CSV header
        # Also store the field type of each header internally in object instance
        notInHeaders = [ ]
        for field in self.fields:
            if not field in self.headers:
                notInHeaders.append(field)
        # Check that all CSV heades are in the table fields
        notInFields = [ ]
        for header in self.headers:
            if not header in self.fields:
                notInFields.append(header)
        # Return error message to user if there are mismatchs between CSV headers and table fields
        if len(notInFields) != 0 and len(notInHeaders) != 0:     
            return "Table fields not in CSV headers: " + ", ".join(notInHeaders) + "; CSV headers not in table fields: " + ", ".join(notInFields)
        elif len(notInFields) != 0:
            "CSV headers not in table fields: " + ", ".join(notInFields)
        elif len(notInHeaders) != 0:
            return "Table fields not in CSV headers:" + ", ".join(notInHeaders)
        else: 
            return ""
    
    def get_foreign_keys(self):
        """Load foreignkeys from foreign models for all fields defined as foreign keys.
        Return error message (string) and field name of id/label (dict)"""
        id_labels_dict = { }
        for field in self.fields:
            if self.field_types[field] == "ForeignKey":
#                try:
                foreign_model = apps.get_model('items',field)
                id_labels_dict[field] = foreign_model.get_id_labels_dict(foreign_model)
#                except:
#                    return ("Error in retrieving foreign keys. Please check label spelling of foreign key fields in models.py: " +  str(id_labels_dict), { } )
        return ("",id_labels_dict)
        
    def line_to_dict(self,line):
        """Splits a CSV line (string) into cells and checks that the cell conforms to the Model's field
        Returns a field dict of values for the row, and a field dict of error messages if any cell did not conform."""
        row = { }
        error = { }
        cells = line.split("\t")
    
        for i in range(0, len(cells)):
            field = self.headers[i]
            field_type = self.field_types[field]
# Make sure all relavant text field types are represented here
            if field_type in [ 'ForeignKey' ]:
                try:
                    row[field + "_id" ] = self.foreign_keys[field][cells[i].strip()]
                except: 
                    print("Field types" + str(self.field_types))
                    print("Cells: " + str(cells))
                    print("Foreign Keys: " + str(self.foreign_keys))
                    row[field] = "Not a foreign key in " + field + ": "+ cells[i] + "; "
                    error[field] = row[field]
                    print(error)
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
        return (row,error)
    
    def parse_lines(self):
        """Parse all data lines to the row to dict splitter."""
# Consider adding a check whether the label already exists - 
# Then add existing labels to one list, and new labels to another
# Do not add rows where data is identical to existing DB rows 
        error_message = ""
        i = 0
        for line in self.lines:
            (row,error) = self.line_to_dict(line)
            self.rows.append(row)
            self.errors.append(error)
            i = i + 1
            if "; ".join(error) != "":
                error_message = error_message  + "There were errors in parsing the data in line " + str(i) + "<BR>" + "; ".join(error)
            else:
                error_message = ""
        return error_message                

# NOTE: If label exists already, we should update the row instead of inserting a new
#       Thus we will avoid breaking primary key relations to other tables
#       How about excessive existing DB rows that are not in the CSV rows - should probably be deleted with cascading effect
#       Perhaps consider to shift the burden of integer primary key to the user?
#       This problem is perhaps only present for "items", but not for other model types?
    def save_objects(self):
        error_message = ""
        def make_error_message(error_type,model_name,row,error_dict):
            em = ["","",""]
            em[0] = error_type + " when uploading CSV table to " + model_name
            em[1] = " in the row["  + " , ".join(row) + "]"
            em[2] = " with the error message " + str(error_dict)
            return "".join(em)
        ItemModel = apps.get_model('items',self.model_name)
        own_keys = ItemModel.get_id_labels_dict(ItemModel)
# example from http://voorloopnul.com/blog/doing-bulk-update-and-bulk-create-with-django-orm/
        with transaction.atomic():
            try:            
# Row is a list of dicts containing values for all fields by field name
                for row in self.rows:
                    print(row)
                    item = ItemModel(**row)
                    try:
                        item.clean_fields()
                        item.clean()
                        item.validate_unique()
                    except ValidationError as e:
                        error_message =  make_error_message("Validation error",self.model_name,row,e)
    
                    item.save()
            except IntegrityError as e:
                error_message =  make_error_message("Integrity error",self.model_name,row,e)
        return error_message