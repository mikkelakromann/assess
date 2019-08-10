import pandas
from xlsxwriter.utility import xl_range, xl_col_to_name

from django.http import HttpResponse 
from django.apps import apps
from django.db.models import Max, F 

from . version import Version
from . tableIO import AssessTableIO

        
class xlsIO():
    """Read/write the tables of an app from/to Excel 2007+."""
    
    def __init__(self, app_name: str, delimiters: dict, ver_str: str) -> None:
        """Initialise from the name of the app."""
        
        self.version = Version()                # Version object
        self.version.set_version_id(ver_str)
        self.models = apps.get_app_config(app_name).get_models() # Model list
        self.dataframes = []                    # Dataframes model equivalents
        self.delimiters = delimiters            # Expected Excel delimiters
        self.metadata = []                      # List of dicts for meta-data



    def get_response(self) -> object:
        """Write app's database tables to Excel file returning Excel file."""

        # Create HTTP response for downloading Excel file
        ct = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=ct)
        response['Content-Disposition'] = "attachment; filename=test.xlsx"
        
        # Link xlswriter to write to the response
        o = {'remove_timezone': True }
        writer = pandas.ExcelWriter(response, engine='xlsxwriter', options=o)

        # Get a dataframe from each of the app's models and write xls sheets
        for model in self.models:
            name = model.__name__
            tIO = AssessTableIO(model, self.delimiters)
            model_df = tIO.get_dataframe(self.version)
            # Convert value column from Decimal to float, required by xlswriter
            if model.value_field in model_df:
                vf = model.value_field
                model_df[vf] = model_df[vf].astype(float)
            # Write dataframe to sheet and define a named range for it
            o = {}
            o['sheet_name'] = name
            o['header'] = False
            o['index'] = False
            o['startrow'] = 1
            model_df.to_excel(writer, **o)

            # Write column headers
            worksheet = writer.sheets[name]
            c = 0
            for field in model.index_fields:
                worksheet.write(0,c,field)
                c = c+1

            # Identify the record with the latest version for getting metadata
            query = model.objects.annotate(latest=Max('version_first__id')) \
                                 .filter(version_first__id=F('latest'))

            metadata_dict = {}
            for record in query:
                metadata_dict['name'] = name
                # TODO: Also include metadata from the metadata model 
                metadata_dict['lastuser'] = record.version_first.user
                metadata_dict['date'] = record.version_first.date
                metadata_dict['dimension'] = record.version_first.dimension
                metadata_dict['size'] = record.version_first.size
                metadata_dict['cells'] = record.version_first.cells
                metadata_dict['changes'] = record.version_first.changes
                metadata_dict['metric'] = float(record.version_first.metric)
            
            self.metadata.append(metadata_dict)
        
        # Load metadata dict into a dataframe and write it to Excel
        meta_df = pandas.DataFrame(self.metadata)
        meta_df.to_excel(writer,sheet_name='metadata')
        # Set some reasonable formats
        writer.book.formats[0].set_bg_color('#dddddd')

        writer.save()
        writer.close()
        return response


    def read(self) -> list:
        """Read Excel file into database for app returning."""
        
        pass