from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.apps import apps
from . models import GetDataNames
from base.table import AssessTable
from base.models import Version
from base.history import History


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

def DataTableView(request,model,col="",ver=""):
    context = { }
    datatable = AssessTable(model)
    datatable.load_model(ver)
    datatable.pivot_1dim(col)
    context['rows'] = datatable.rows
    context['headers'] = datatable.headers
    context['model_name'] = datatable.model_name
    history = History(datatable.model)
    context['history'] = history.context_data 
    context['version_name'] = datatable.version
    return render(request, 'data_table.html', context )
        

########################
# UploadView
########################

def DataUploadView(request, model):
    context = { }
    model_name = model._meta.object_name.lower()
    if request.method == 'GET':
        return render(request, 'data_upload_form.html', {'model_name': model_name })
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
        
def DataCommitView(request, model):
    context = { }
    model_name = model._meta.object_name.lower()
    datatable = AssessTable(model)
    datatable.load_model("current")
    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
    else:
        if request.method == 'GET':
            return render(request, 'data_commit_form.html', {'model_name': model_name })
        elif request.method == 'POST':
            version_info = {}
            version_info['label'] = request.POST['label']
            version_info['user'] = request.POST['user']
            version_info['note'] = request.POST['note']
            datatable.commit_rows(version_info)
    # Print current table in any case
    datatable.pivot_1dim("")
    context['model_name'] = datatable.model_name
    context['rows'] = datatable.rows
    context['headers'] = datatable.headers
    history = History(datatable.model)
    context['history'] = history.context_data 
    context['version_name'] = "current"
    return render(request, 'data_table.html', context )


def DataRevertView(request, model):
    pass
