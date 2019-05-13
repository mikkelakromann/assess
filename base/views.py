from django.shortcuts import render
from django.apps import apps
from django.http import Http404

from base.table import AssessTable
from base.tableIO import AssessTableIO
from base.collection import AssessCollection


def BaseIndexView(request):
    """Dummy index view to be remvoed."""
    return render(request, 'base_index.html')


def get_model_name_dicts(app_name,suffix,model_types):
    """
    Return side bar nagivation context dictionary of 
    model names and url names in app_name.
    """
    
    links = [ ] 
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        if m.model_type in model_types:
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


def get_navigation_links(app_name,suffix,model_types):
    """Return context dict with navigation link"""
    
    context = {}
    context['item_links'] = get_model_name_dicts(app_name,'_list','item_model')
    context['data_links'] = get_model_name_dicts(app_name,'_table','data_model')
    context['topbar_links'] = get_top_bar_links(app_name)
    return context


def TableDisplayView(request,model,app_name,col="",ver="",dif=""):
    """View for displaying data table content."""

    datatable = AssessCollection(model,ver)
    datatable.load(dif,[])
    datatable.set_rows(col)
    context = get_navigation_links(app_name, '_table',['data_model'])
    context.update(datatable.get_context())
    return render(request, 'data_display.html', context)


def TableUploadView(request,model,app_name):
    """View for uploading data table content."""

    model_name = model._meta.object_name.lower()
    context = get_navigation_links(app_name,'_table',['data_model'])
    context['model_name'] = model_name 
    if request.method == 'GET':
        col_list = []
        for column in model.index_fields + [model.value_field]:
            col_dict = {}
            col_dict['label'] = column
            col_dict['name'] = column.capitalize()
            if column == model.column_field:
                col_dict['checked'] = ' checked'
            col_list.append(col_dict)
        context['column_field_choices'] = col_list
        return render(request, 'data_upload_form.html', context )
    elif request.method == 'POST':
        # TO-DO: Fetch delimiters from user preferences or POST string
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        tableIO = AssessTableIO(model)
        records = tableIO.parse_csv(request,delimiters)
        datatable = AssessCollection(model,"proposed")
        datatable.load(False)
        datatable.save_changed_records(records)
        context.update(datatable.get_context())
        return render(request, 'data_display.html', context)
    else:
        Http404("Invalid HTTP method.")
        
def TableCommitView(request,model,app_name):
    """
    View for committing data table content.
    """

    model_name = model._meta.object_name.lower()
    datatable = AssessCollection(model)
    context = get_navigation_links(app_name,'_table',['data_model'])
    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context['model_name'] = model_name 
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
        datatable.load("current")
        datatable.pivot_1dim("")
        context.update(datatable.get_context('data'))
        return render(request, 'data_table.html', context)
    else:
        if request.method == 'GET':
            context['model_name'] = model_name 
            return render(request, 'data_commit_form.html', context )
        elif request.method == 'POST':
            version_info = {}
            version_info['label'] = request.POST['label']
            version_info['user'] = request.POST['user']
            version_info['note'] = request.POST['note']
            datatable.commit_rows(version_info)
            datatable.load("current")
            datatable.pivot_1dim("")
            context.update(datatable.get_context())
            return render(request, 'data_display.html', context)

def TableRevertView(request, model,app_name):
    """
    View for reverting data table content.
    """

    datatable = AssessTable(model)
    datatable.revert_proposed()
    datatable.load_model("current")
    datatable.pivot_1dim("")
    context = get_navigation_links(app_name,'_table',['data_model'])
    context.update(datatable.get_context('data'))
    return render(request, 'data_display.html', context)
