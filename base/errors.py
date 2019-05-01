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
        self.model_name = model.__name__
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
        self.model_name = model.__name__
        self.message = field_name + " does not exist in " + self.model_name
        
    def __str__(self):
        return self.message

    
class NoModelError(AssessError):
    """Exception raised for looking up missing model in app
    
    Attributes
        model_name: model that supposedly should have had item
        app_name: item asked for but not found
    """
    
    def __init__(self,model,app_name):
        self.app_name = app_name
        self.model_name = model.__name__
        self.message = self.model_name + " does not exist in " + app_name
        
    def __str__(self):
        return self.message
    

class NotCleanRecord(AssessError):
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


class NoRecordIntegrity(AssessError):
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
    
class CSVlineWrongCount(AssessError):
    """Exception raised CSV line that has not same column count as CSV header
    
    Attributes
        record: model that supposedly should have had item
        app_name: item asked for but not found
        line: string with malformed CSV line
    """
    
    def __init__(self,model,csv_line,csv_header):
        self.app_name = model._meta.app_label
        self.model_name = model.__name__
        self.message = self.model_name + " / " + self.app_name + \
                       ": The CSV line cell count did not match the "+  \
                       " CSV header cell count. CSV header: " + csv_header + \
                       " CSV line: " + csv_line 
        
    def __str__(self):
        return self.message    
    

class CSVheaderNotFound(AssessError):
    """Exception raised CSV line that has not same column count as CSV header
    
    Attributes
        record: model that supposedly should have had item
        app_name: item asked for but not found
        line: string with malformed CSV line
    """
    
    def __init__(self,record,error):
        self.app_name = record.app_name
        self.model_name = record.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       ": The records had lacking integrity: "+  \
                       str(error) + str(record) 
        
    def __str__(self):
        return self.message    


class CSVfieldNotFound(AssessError):
    """Exception raised CSV line that has not same column count as CSV header
    
    Attributes
        record: model that supposedly should have had item
        app_name: item asked for but not found
        line: string with malformed CSV line
    """
    
    def __init__(self,record,error):
        self.app_name = record.app_name
        self.model_name = record.model_name
        self.message = self.model_name + " / " + self.app_name + \
                       ": The records had lacking integrity: "+  \
                       str(error) + str(record) 
        
    def __str__(self):
        return self.message    
