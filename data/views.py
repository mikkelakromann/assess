from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.apps import apps
from . models import GetDataNames
from base.csv import csv_to_list_of_dicts
from base.table import AssessTable

# Create your views here.

# The value of the dictionary is used for displaying the name of the model, so call it something human readable
def GetDataDictionary(request):
    d1 = [ ] 
    for d in GetDataNames():
        d1.append( { 'name': d.lower(), 'readable': d, 'urlname': d.lower() + '_table' } )
    return { 'dataDictionary': d1 }

########################
# ItemIndex - Front page for items
########################
def DataIndexView(request):
    context = { }
    i = { }
    i = GetDataDictionary(request)
    context['dataDictionary'] = i['dataDictionary']
    return render(request, 'data_index.html', context )

########################
# TableView
########################

class DataTableView(ListView):
    fields = None
    template_name = "data_table.html"        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = AssessTable(self.model)
        table.load_records()
        table.pivot_1dim(self.model.column_field)
        context['model_name'] = table.model_name
        context['rows'] = table.rows
        context['headers'] = list(table.headers)
        return context
        

########################
# UploadView
########################

def DataUploadView(request, data_name):
    error_message = ""
    context = { }
    try:
        Data = apps.get_model('data',data_name)
    except:
        Http404("Table " + data_name + "does not exist!")

    if request.method == 'GET':
        return render(request, 'data_upload_form.html', {'data_name': data_name.lower })
    elif request.method == 'POST':
        delimiters = {'decimal': ',', 'thousand': '.' }
        csv = csv_to_list_of_dicts(request.POST['csvtable'],Data,delimiters)
        Data.import_rows(csv.rows)
        context['row_list'] = csv.rows 
        context['field_list'] = csv.fields
        context['model_name'] = data_name
        context['error_message'] = error_message
        return render(request, 'data_upload_result.html', context )
    else:
        Http404("Invalid HTTP method.")
