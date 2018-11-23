from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.apps import apps
from . models import GetDataNames
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

def DataTableView(request,model,col=""):
    context = { }
    # Beware! If model.fields include a non-model choice field, table.pivot will fail
    if col == "" or not col in model.fields:
        column_field = model.fields[-2]
    else:
        column_field = col
    datatable = AssessTable(model)
    datatable.load_model()
    datatable.pivot_1dim(column_field)
    context['model_name'] = datatable.model_name
    context['rows'] = datatable.rows
    context['headers'] = datatable.headers
    return render(request, 'data_table.html', context )
        

########################
# UploadView
########################

def DataUploadView(request, data_name):
    error_message = ""
    context = { }
    try:
        model = apps.get_model('data',data_name)
    except:
        Http404("Table " + data_name + "does not exist!")
    if request.method == 'GET':
        return render(request, 'data_upload_form.html', {'data_name': data_name.lower })
    elif request.method == 'POST':
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        datatable = AssessTable(model)
        datatable.load_csv(request.POST['csv_string'],delimiters)
        datatable.save_dataframe()
        context['rows'] = datatable.rows 
        context['fields'] = datatable.fields
        context['model_name'] = datatable.model_name
        return render(request, 'data_upload_result.html', context )
    else:
        Http404("Invalid HTTP method.")
