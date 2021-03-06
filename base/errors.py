class AssessError(Exception):
    pass

class NoItemError(AssessError):
    """Exception raised for looking up non-existing item in model

    Attributes
        item_name: item asked for but not found
        model_name: model that supposedly should have had item
    """
    def __init__(self,item_name,model):
        self.item_name = item_name
        self.model_name = model.model_name
        self.message = item_name + " does not exist in " + self.model_name

    def __str__(self):
        return self.message

class NoFieldError(AssessError):
    """Exception raised for looking up non-existing field in model

    Attributes
        item_name: item asked for but not found
        model_name: model that supposedly should have had item
    """
    def __init__(self,field_name,model):
        self.field_name = field_name
        self.model_name = model.model_name
        self.message = field_name + " does not exist in " + self.model_name

    def __str__(self):
        return self.message

class NotDecimalError(AssessError):
    """Exception raised for entering malformed decimal string

    Attributes
        model_name: model that supposedly should have had item
        app_name: item asked for but not found
    """
    def __init__(self,decimal_str,model):
        self.app_name = model.app_name
        self.model_name = model.model_name
        self.message = decimal_str + " could not be converted to decimal" +\
                       "in " + self.model_name
    def __str__(self):
        return self.message

# TODO: Find test for this
class NotCleanRecord(AssessError): # pragma: no cover
    """Exception raised for for saving not clean record

    Attributes
        model_name: model that supposedly should have had item
        app_name: item asked for but not found
    """
    def __init__(self,record,error):
        self.app_name = record.app_name
        self.model_name = record.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       ": The record was not clean: " + \
                       str(error) + str(record)

    def __str__(self):
        return self.message

# TODO: Find test for this
class NoRecordIntegrity(AssessError): # pragma: no cover
    """Exception raised for missing record integrity

    Attributes
        record: model that supposedly should have had item
        app_name: item asked for but not found
    """
    def __init__(self,record,error):
        self.app_name = record.model._meta.app_label
        self.model_name = record.model.__name__
        self.message = self.model_name + " / " + self.app_name + \
                       ": The records had lacking integrity: "+  \
                       str(error) + str(record)

    def __str__(self):
        return self.message

class CSVwrongColumnCount(AssessError):
    """Exception raised CSV line that has not same column count as CSV header

    Attributes
        cells: list of index and value cell contents in CSV table
        csv_headers: list of elements in CSV file header
        msg: str of error message from any other error message raised earlier
        model: object of type AssessModel
    """
    def __init__(self,cells,csv_headers,msg,model):
        self.app_name = model._meta.app_label
        self.model_name = model.__name__
        self.message = self.model_name + " / " + self.app_name + \
                       ": The CSV line cell count did not match the "+  \
                       " CSV header cell count. CSV header: " +  \
                       str(csv_headers) + " CSV line: " + str(cells)

    def __str__(self):
        return self.message


class CSVheaderMalformed(AssessError):
    """Exception raised CSV header has bad field names or items in it

    Attributes
        csv_header_list: list of elements in CSV file header
        table_header_list: list of items expected for the table
        msg: str of error message from any other error message raised earlier
        model: object of type AssessModel
    """
    def __init__(self, csv_header_list, table_header_list, msg, model):
        self.app_name = model._meta.app_label
        self.model_name = model.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       ": At line 1" + \
                       " the CSV header list " + str(csv_header_list) + \
                       " did not match the table header list " + \
                       str(table_header_list) + ". " + msg 

    def __str__(self):
        return self.message

class CSVfieldNotFound(AssessError):
    """Exception raised CSV line that has not same column count as CSV header

    Attributes
        record: model that supposedly should have had item
        app_name: item asked for but not found
        line: string with malformed CSV line
    """
    def __init__(self, csv_row_list, table_header_list, msg, model):
        self.app_name = model._meta.app_label
        self.model_name = model.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       " The CSV row " + str(csv_row_list) + \
                       " did not match the table header list " + \
                       str(table_header_list) + ". " + msg 

    def __str__(self):
        return self.message


class KeyNotFound(AssessError):
    """Exception raised for key string in POST that did not match items

    Attributes
        key_str: parsed key string
        model: model class
        line: string with malformed CSV line
    """
    def __init__(self,key_str,model):
        self.app_name = model.app_name
        self.model_name = model.model_name
        fields = model.index_fields.copy()
        fields.append(model.value_field)
        self.message = self.model_name + " / " + self.app_name + \
                       ": Mismatch between key string and model fields: "+  \
                       str(key_str) + ' != ' + str(fields)

    def __str__(self):
        return self.message


class KeyInvalid(AssessError):
    """Exception raised for key string in POST that did not match items

    Attributes
        key_str: parsed key string
        model: model class
        line: string with malformed CSV line
    """
    def __init__(self,key_str,model):
        self.app_name = model.app_name
        self.model_name = model.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       ": The key string format is invalid: "+  \
                       str(key_str)

    def __str__(self):
        return self.message


