from django.http import Http404
from django.shortcuts import render
from base.views import get_model_name_dicts, get_navigation_links
from base.table import AssessTable


# Create your views here.

# The value of the dictionary is used for displaying the name of the model, so call it something human readable
def GetDataDictionary(request):
    d1 = [ ] 
    for d in GetDataNames():
        d1.append( { 'name': d.lower(), 'readable': d, 'urlname': d.lower() + '_table' } )
    return { 'dataDictionary': d1 }

def DataIndexView(request):
    context = get_navigation_links('data','_table')
    return render(request, 'data_index.html', context )

def DataTableView(request,model,app_name,col="",ver="",dif=""):
    datatable = AssessTable(model)
    datatable.load_model(ver,dif)
    datatable.pivot_1dim(col)
    return render(request, 'data_table.html', datatable.get_context('data'))

def DataUploadView(request,model,app_name):
    model_name = model._meta.object_name.lower()
    if request.method == 'GET':
        context = get_navigation_links('data','_table')
        context['model_name'] = model_name 
        return render(request, 'data_upload_form.html', context )
    elif request.method == 'POST':
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        datatable = AssessTable(model)
        datatable.load_csv(request.POST['csv_string'],delimiters)
        datatable.save_dataframe()
        datatable.load_model("proposed")
        datatable.pivot_1dim("")
        return render(request, 'data_table.html', datatable.get_context('data'))
    else:
        Http404("Invalid HTTP method.")
        
def DataCommitView(request,model,app_name):
    model_name = model._meta.object_name.lower()
    datatable = AssessTable(model)
    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context = get_navigation_links('data','_table')
        context['model_name'] = model_name 
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
        datatable.load_model("current")
        datatable.pivot_1dim("")
        return render(request, 'data_table.html', dict(context,datatable.get_context('data')) )
    else:
        if request.method == 'GET':
            context = get_navigation_links('data','_table')
            context['model_name'] = model_name 
            return render(request, 'data_commit_form.html', context )
        elif request.method == 'POST':
            version_info = {}
            version_info['label'] = request.POST['label']
            version_info['user'] = request.POST['user']
            version_info['note'] = request.POST['note']
            datatable.commit_rows(version_info)
            datatable.load_model("current")
            datatable.pivot_1dim("")
            return render(request, 'data_table.html', datatable.get_context('data'))

def DataRevertView(request, model,app_name):
    datatable = AssessTable(model)
    datatable.revert_proposed()
    datatable.load_model("current")
    datatable.pivot_1dim("")
    return render(request, 'data_table.html', datatable.get_context('data'))
