from django.shortcuts import render
from django.apps import apps
from django.http import Http404

from base.table import AssessTable


def BaseIndexView(request):
    """Dummy index view to be remvoed."""
    return render(request, 'base_index.html')


def get_model_name_dicts(app_name,suffix):
    """
    Return side bar nagivation context dictionary of 
    model names and url names in app_name.
    """
    
    links = [ ] 
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + suffix } )
    return links


def get_top_bar_links(app_name):
    """
    Return top bar nagivation context as dictionary 
    of model names and url names in app_name.
    """
    links = [ ]
    for n in ['Items', 'Data', 'Choices', 'Scenarios', 'Results' ]:
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + '_index' } )
    return links    


def get_navigation_links(app_name,suffix):
    """
    Return context dict with navigation link
    """
    
    context = {}
    context['sidebar_links'] = get_model_name_dicts(app_name,suffix)
    context['topbar_links'] = get_top_bar_links(app_name)
    return context


def TableDisplayView(request,model,app_name,col="",ver="",dif=""):
    """
    View for displaying data table content.
    """

    datatable = AssessTable(model)
    datatable.load_model(ver,dif)
    datatable.pivot_1dim(col)
    context = get_navigation_links(app_name, '_table')
    context.update(datatable.get_context('data'))
    return render(request, 'data_table.html', context)

def TableUploadView(request,model,app_name):
    """
    View for uploading data table content.
    """

    model_name = model._meta.object_name.lower()
    if request.method == 'GET':
        context = get_navigation_links(app_name,'_table')
        context['model_name'] = model_name 
        return render(request, 'data_upload_form.html', context )
    elif request.method == 'POST':
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        datatable = AssessTable(model)
        datatable.load_csv(request.POST['csv_string'],delimiters)
        datatable.save_dataframe()
        datatable.load_model("proposed")
        datatable.pivot_1dim("")
        context = get_navigation_links(app_name)
        context.update(datatable.get_context('data'))
        return render(request, 'data_table.html', context)
    else:
        Http404("Invalid HTTP method.")
        
def TableCommitView(request,model,app_name):
    """
    View for committing data table content.
    """

    model_name = model._meta.object_name.lower()
    datatable = AssessTable(model)
    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context = get_navigation_links(app_name,'_table')
        context['model_name'] = model_name 
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
        datatable.load_model("current")
        datatable.pivot_1dim("")
        context = get_navigation_links(app_name)
        context.update(datatable.get_context('data'))
        return render(request, 'data_table.html', context)
    else:
        if request.method == 'GET':
            context = get_navigation_links(app_name,'_table')
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
            context = get_navigation_links(app_name)
            context.update(datatable.get_context('data'))
            return render(request, 'data_table.html', context)

def TableRevertView(request, model,app_name):
    """
    View for reverting data table content.
    """

    datatable = AssessTable(model)
    datatable.revert_proposed()
    datatable.load_model("current")
    datatable.pivot_1dim("")
    context = get_navigation_links(app_name)
    context.update(datatable.get_context('data'))
    return render(request, 'data_table.html', context)
