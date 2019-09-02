import pandas

from django.http import HttpResponse
from django.apps import apps
from django.db.models import Max, F

from . version import Version
from . tableIO import AssessTableIO
from . table import AssessTable


class XlsIO():
    """Read/write the tables of an app from/to Excel 2007+."""
    def __init__(self, app_name: str, delimiters: dict, ver_str: str) -> None:
        """Initialise from the name of the app."""
        self.app_name = app_name
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
        response['Content-Disposition'] = "attachment; filename=" + self.app_name + ".xlsx"
        # Link xlswriter to write to the response
        o = {'remove_timezone': True }
        writer = pandas.ExcelWriter(response, engine='xlsxwriter', options=o)
        # Get a dataframe from each of the app's models and write xls sheets
        error = ""
        for model in self.models:
            name = model.__name__
            if model.model_type in ['data_model','mappings_model']:
                tIO = AssessTableIO(model, self.delimiters)
                model_df = tIO.get_dataframe(self.version)
            if model.model_type == 'item_model':
                query = model.objects.values('label')
                items = []
                for record in query:
                    items.append(record['label'])
                model_df = pandas.DataFrame(items)
            if model.model_type == 'data_model':
                # xlswriter needs converting value column from Decimal to float
                if model.value_field in model_df:
                    vf = model.value_field
                    model_df[vf] = model_df[vf].astype(float)
                else:
                    error = 'No value column in data_model ' + name
            # Write dataframe to sheet and define a named range for it
            o = {'header': False, 'index': False, 'startrow': 0}
            o['sheet_name'] = name
            model_df.to_excel(writer, **o)
            # Write column headers
            if model.model_type != 'item_model':
                worksheet = writer.sheets[name]
                c = 0
                for field in model.index_fields:
                    worksheet.write(0,c,field)
                    c = c+1
            # Identify the record with the latest version for getting metadata
            query = model.objects.annotate(latest=Max('version_first__id')) \
                                 .filter(version_first__id=F('latest'))
            metadata_dict = {'name': name, 'error': error }
            # The query should hold exactly one record
            for record in query:
                # TODO: Also include metadata from the metadata model
                metadata_dict['lastuser'] = record.version_first.user
                metadata_dict['date'] = record.version_first.date
                metadata_dict['dimension'] = record.version_first.dimension
                metadata_dict['size'] = record.version_first.size
                metadata_dict['cells'] = record.version_first.cells
                metadata_dict['changes'] = record.version_first.changes
                if record.version_first.metric:
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

    def parse_save(self, excel_file) -> list:
        """Read Excel file into database for app returning list of errors."""
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        report_list = []
        for model in self.models:
            name = model.__name__
            report_dict = { 'read_errors': '', 'proposed': 0, 'parse_errors': ''}
            report_dict['name'] = name
            try:
                model_df = pandas.read_excel(excel_file, sheet_name=name, index_col=None)
            except Exception as e:
                # TODO: Find out how to pass error messages to the uesr
                report_dict['read_errors'] = str(e)
            else:
                if model.model_type == 'item_model':
                    # TODO: Allow importing of item_models from Excel
                    pass
                else:
                    tableIO = AssessTableIO(model,delimiters)
                    records = tableIO.parse_dataframe(model_df)
                    # TODO: Check that the dataframe was error free
                    if tableIO.errors == []:
                        table = AssessTable(model,'proposed')
                        table.load(False)
                        table.save_changed_records(records)
                        report_dict['proposed'] = table.proposed_count()
                    else:
                        # TODO: Find out how to pass error messages to the uesr
                        report_dict['parse_errors'] = str(tableIO.errors)
            report_list.append(report_dict)
        return report_list
