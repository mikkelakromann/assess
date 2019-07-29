from django.shortcuts import render
from django.apps import apps
from django.urls import path
from django.http import Http404

from . tableIO import AssessTableIO
from . table import AssessTable
from . messages import Messages

def get_url_paths(app_name):
    """Produce set of url pattern paths for each model in the data app."""

    paths = []
    kwargs1 = { 'app_name': app_name }
    paths.append(path( 'index',                             IndexView,          kwargs1, name=app_name+'_index' ) )

    # get_models() return Model Class, not object instance
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        nL = n.lower()
        m.app_name = app_name
        m.model_name = m.__name__
        if m.model_type == 'item_model':
            kwargs1 = { 'model': m, 'app_name': app_name }
            paths.append(path( 'list/'+nL+'/' ,             ItemListView,       kwargs1, name=nL+'_list'   ) )
            paths.append(path( 'create/'+nL+'/',            ItemCreateView,     kwargs1, name=nL+'_create' ) )
            paths.append(path( 'update/'+nL+'/<pk>/',       ItemUpdateView,     kwargs1, name=nL+'_update' ) )
            paths.append(path( 'delete/'+nL+'/<pk>/',       ItemDeleteView,     kwargs1, name=nL+'_delete' ) )
            paths.append(path( 'upload/'+nL+'/',            ItemUploadView,     kwargs1, name=nL+'_upload' ) )

        if m.model_type == 'data_model' or m.model_type == 'mappings_model':
            kwargs1 = { 'model': m, 'app_name':  app_name }
            kwargs2 = { 'model': m, 'app_name':  app_name, 'dif': False }
            kwargs3 = { 'model': m, 'app_name':  app_name, 'dif': True  }
            paths.append(path( nL+'/commit/',               TableCommitView,    kwargs1, name=nL+'_commit'  ) )
            paths.append(path( nL+'/revert/',               TableRevertView,    kwargs1, name=nL+'_revert'  ) )
            paths.append(path( nL+'/upload/',               TableUploadView,    kwargs1, name=nL+'_upload'  ) )
            paths.append(path( nL+'/edit/',                 TableEditView,      kwargs1, name=nL+'_edit'    ) )
            paths.append(path( nL+'/edit/<str:col>/',       TableEditView,      kwargs1, name=nL+'_edit'    ) )
            paths.append(path( nL+'/',                      TableDisplayView,   kwargs2, name=nL+'_table'   ) )
            paths.append(path( nL+'/<str:ver>/',            TableDisplayView,   kwargs2, name=nL+'_version' ) )
            paths.append(path( nL+'/<str:ver>/change/',     TableDisplayView,   kwargs3, name=nL+'_change'  ) )
            paths.append(path( nL+'/<str:ver>/<str:col>/',  TableDisplayView,   kwargs2, name=nL+'_version' ) )

    return paths


def IndexView(request,app_name):
    """Show list of items, mappings and data tables with links+descriptions."""

    context = get_navigation_links(app_name)
    return render(request, app_name + '_index.html', context )



def BaseIndexView(request):
    """Dummy index view to be remvoed."""
    return render(request, 'base_index.html')


def get_model_name_dicts(app_name,suffix,model_type):
    """Return side bar nagivation dict for all app tables."""

    links = [ ]
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        if m.model_type == model_type:
            links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + suffix } )
    return links


def get_top_bar_links(app_name):
    """Return top bar nagivation links for each app."""
    links = [ ]
    for n in ['Items', 'Data', 'Choices', 'Scenarios', 'Results' ]:
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + '_index' } )
    return links


def get_navigation_links(app_name):
    """Return context dict with navigation link"""

    context = {}
    context['item_links'] = get_model_name_dicts(app_name,'_list','item_model')
    context['data_links'] = get_model_name_dicts(app_name,'_table','data_model')
    context['mappings_links'] = get_model_name_dicts(app_name,'_table','mappings_model')
    context['topbar_links'] = get_top_bar_links(app_name)
    return context


def TableDisplayView(request,model,app_name,col="",ver="",dif=""):
    """View for displaying data table content."""

    datatable = AssessTable(model,ver)
    datatable.load(dif,[])
    datatable.set_rows(col,'display')
    context = get_navigation_links(app_name)
    context.update(datatable.get_context())
    return render(request, 'data_display.html', context)


def TableEditView(request,model,app_name,col=""):
    """View for editing data table content."""

    model_name = model._meta.object_name.lower()
    context = get_navigation_links(app_name)
    context['model_name'] = model_name
    if request.method == 'POST':
        delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
        tableIO = AssessTableIO(model,delimiters)
        records = tableIO.parse_POST(request.POST)
        datatable = AssessTable(model,"proposed")
        datatable.load(False)
        datatable.save_changed_records(records)
        datatable.load(False)
        datatable.set_rows("",'display')
        context.update(datatable.get_context())
        return render(request, 'data_display.html', context)
    else:
        datatable = AssessTable(model,'current')
        datatable.load(False,[])
        datatable.set_rows(col,'update')
        context = get_navigation_links(app_name)
        context.update(datatable.get_context())
        return render(request, 'data_edit.html', context)


def TableUploadView(request,model,app_name):
    """View for uploading data table content."""

    model_name = model._meta.object_name.lower()
    context = get_navigation_links(app_name)
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
        tableIO = AssessTableIO(model,delimiters)
        records = tableIO.parse_csv(request.POST)
        datatable = AssessTable(model,"proposed")
        datatable.load(False)
        datatable.save_changed_records(records)
        datatable.load(False)
        datatable.set_rows("",'display')
        context.update(datatable.get_context())
        return render(request, 'data_display.html', context)
    else:
        Http404("Invalid HTTP method.")


def TableCommitView(request,model,app_name):
    """View for committing data table content."""

    model_name = model._meta.object_name.lower()
    datatable = AssessTable(model,"proposed")
    context = get_navigation_links(app_name)
    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context['model_name'] = model_name
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
        datatable.load(False)
        datatable.set_rows("",'display')
        context.update(datatable.get_context())
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
            datatable.load(False)
            datatable.set_rows("",'display')
            context.update(datatable.get_context())
            return render(request, 'data_display.html', context)

def TableRevertView(request, model,app_name):
    """View for reverting data table content."""

    datatable = AssessTable(model,"proposed")
    datatable.revert_proposed()
    datatable.load(False)
    datatable.set_rows("",'display')
    context = get_navigation_links(app_name)
    context.update(datatable.get_context())
    return render(request, 'data_display.html', context)


def ItemIndexView(request):
    """View for listing all item models."""

    context = get_navigation_links("items")
    return render(request, 'item_index.html', context )


def ItemListView(request, model, app_name):
    """Render table with all current items."""

    model.model_name = model._meta.object_name.lower()
    context = { }
    context.update(get_navigation_links(app_name))
    context.update(model.get_current_list_context(model))
    context['model_name'] = model.model_name
    return render(request, 'item_list.html', context )


def ItemDeleteView(request, pk, model, app_name):
    """Returns views for deleting items."""

    context = get_navigation_links(app_name)
    model.model_name = model._meta.object_name.lower()
    context['model_name'] = model.model_name
    context['item_id'] = pk
    message = Messages()
    if request.method == 'GET':
        item_label = model.get_label(model,pk)
        context['item_label'] = item_label
        d = { 'item_label': item_label, 'model_name': model.model_name }
        context['item_delete_heading'] = message.get('item_delete_heading',d)
        context['item_delete_notice'] = message.get('item_delete_notice',d)
        context['item_delete_confirm'] = message.get('item_delete_confirm',d)
        context['item_delete_reject'] = message.get('item_delete_reject',d)
        return render(request, 'item_delete_form.html', context )
    elif request.method == 'POST':
        # item.rename() renames item and returns succes or error message
        item_id  = request.POST['id']
        context['message'] = model.delete(model,item_id)
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )
    else:
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )


def ItemUpdateView(request, pk, model, app_name):
    """Returns views for updating item name"""

    context = get_navigation_links(app_name)
    model.model_name = model._meta.object_name.lower()
    context['model_name'] = model.model_name
    context['item_id'] = pk
    if request.method == 'GET':
        context['item_label'] = model.get_label(model,pk)
        return render(request, 'item_update_form.html', context )
    elif request.method == 'POST':
        # item.rename() renames item and returns succes or error message
        item_id  = request.POST['id']
        item_new_label = request.POST['label']
        context['message'] = model.rename(model,item_id,item_new_label)
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )
    else:
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )


def ItemCreateView(request, model, app_name):
    """Return views for creating new items"""

    context = get_navigation_links(app_name)
    model.model_name = model._meta.object_name.lower()
    context['model_name'] = model.model_name
    if request.method == 'GET':
        return render(request, 'item_create_form.html', context )
    elif request.method == 'POST':
        # item.rename() renames item and returns succes or error message
        item_new_label = request.POST['label']
        context['message'] = model.create(model,item_new_label)
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )
    else:
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )


def ItemUploadView(request, model, app_name):
    """Return views for posting CSV string multiple items."""

    context = get_navigation_links(app_name)
    model.model_name = model._meta.object_name.lower()
    context['model_name'] = model.model_name
    if request.method == 'GET':
        return render(request, 'item_upload_form.html', context )
    elif request.method == 'POST':
        # item.rename() renames item and returns succes or error message
        CSVstring = request.POST['CSVstring']
        context['message'] = model.upload(model,CSVstring)
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )
    else:
        context.update(model.get_current_list_context(model))
        return render(request, 'item_list.html', context )

