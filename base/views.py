from django.shortcuts import render
from django.apps import apps
from django.urls import path

from . set import AssessSet
from . table import AssessTable
from . appIO import XlsIO


def get_url_paths(app_name):
    """Produce set of url pattern paths for each model in the data app."""
    paths = []
    kwargs1 = { 'app_name': app_name }
    paths.append(path( 'index',                             IndexView,          kwargs1, name=app_name+'_index' ) )
    paths.append(path( 'xlsdownload/',                      AppXlsDownloadView, kwargs1, name=app_name+'_xlsdownload' ) )
    paths.append(path( 'xlsdownload/<str:ver>/',            AppXlsDownloadView, kwargs1, name=app_name+'_xlsdownload' ) )
    paths.append(path( 'xlsupload/',                        AppXlsUploadView,   kwargs1, name=app_name+'_xlsupload' ) )
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


def get_model_name_dicts(app_name,suffix,model_type):
    """Return side bar nagivation dict for all app tables."""
    links = [ ]
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        if m.model_type == model_type:
            links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + suffix } )
    return links


def get_xls_links(app_name):
    """Return links for uploading and downloading Xls sheets."""
    return  [ { 'readable': 'Download', 'urlname': app_name + '_xlsdownload' },
              { 'readable': 'Upload', 'urlname': app_name + '_xlsupload' }, ]


def get_top_bar_links(app_name):
    """Return top bar nagivation links for each app."""

    links = [ ]
    for n in ['Items', 'Data', 'Choices', 'Scenarios', 'Results' ]:
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + '_index' } )
    return links


def get_navigation_links(app_name):
    """Return context dict with navigation link"""
    context = {}
    context['app_name'] = app_name
    context['item_links'] = get_model_name_dicts(app_name,'_list','item_model')
    context['data_links'] = get_model_name_dicts(app_name,'_table','data_model')
    context['mappings_links'] = get_model_name_dicts(app_name,'_table','mappings_model')
    context['topbar_links'] = get_top_bar_links(app_name)
    context['xls_links'] = get_xls_links(app_name)
    return context


def AssessRender(request, template, context, app_name):
    """Add navigation links to rendering."""
    context.update(get_navigation_links(app_name))
    return render(request, template, context)


def IndexView(request,app_name):
    """Show list of items, mappings and data tables with links+descriptions."""
    context = get_navigation_links(app_name)
    # TODO: Rewrite to generic app index view, delete
    return AssessRender(request, 'app_index.html', context, app_name )


def BaseIndexView(request):
    """Dummy index view to be remvoed."""
    # TODO: Rewrite to generic app index view
    return render(request, 'base_index.html')


def AppXlsDownloadView(request: object, app_name: str, ver='') -> object:
    """View for uploading and downloading Excel tables to and from app DB."""

    delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
    # Create XLS sheet, populate with app data and return as file
    xls = XlsIO(app_name,delimiters,ver)
    return xls.get_response()


def AppXlsUploadView(request: object, app_name: str) -> object:
    """View for uploading and downloading Excel tables to and from app DB."""
    delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
    if request.method == "POST":
        # Parse the provided excel file
        excel_file = request.FILES["excel_file"]
        xlsio = XlsIO(app_name,delimiters,"")
        xlsio.parse_save(excel_file)
        return IndexView(request, app_name)
    else:
        # Provide upload file select view for user
        context = get_navigation_links(app_name)
        return render(request, 'file_upload_form.html', context)


def TableDisplayView(request,model,app_name,col="",ver="",dif=""):
    """View for displaying data table content."""
    datatable = AssessTable(model,ver)
    context = datatable.render_table_context(col,dif,[])
    return AssessRender(request, 'table_display.html', context, app_name)


def TableEditView(request,model,app_name,col=""):
    """View for editing data table content."""
    if request.method == 'POST':
        datatable = AssessTable(model,"proposed")
        datatable.save_POST(request.POST)
        context = datatable.render_table_context(col,False,[])
        return AssessRender(request, 'table_display.html', context, app_name)
    else:
        datatable = AssessTable(model,'current')
        context = datatable.render_table_context(col,False,[])
        return AssessRender(request, 'table_edit.html', context, app_name)


def TableUploadView(request,model,app_name):
    """View for uploading data table content."""
    datatable = AssessTable(model,"proposed")
    if request.method == 'GET':
        context = datatable.get_CSV_form_context()
        return AssessRender(request, 'table_upload_form.html', context, app_name)
    elif request.method == 'POST':
        datatable.save_CSV(request.POST)
        context = datatable.render_table_context("",False,[])
        return AssessRender(request, 'table_display.html', context, app_name)
    else:
        context = datatable.render_table_context("",False,[])
        return AssessRender(request, 'table_display.html', context, app_name)


def TableCommitView(request,model,app_name):
    """View for committing data table content."""
    datatable = AssessTable(model,"proposed")
    # If no new records are proposed, nothing will be committed
    if datatable.proposed_count() == 0:
        context = datatable.render_table_context("",False,[])
        return AssessRender(request, 'table_display.html', context, app_name)
    else:
        if request.method == 'GET':
            context = datatable.get_commit_form_context()
            return AssessRender(request, 'table_commit_form.html', context, app_name)
        elif request.method == 'POST':
            datatable.commit_rows(request.POST)
            context = datatable.render_table_context("",False,[])
            return AssessRender(request, 'table_display.html', context, app_name)


def TableRevertView(request, model,app_name):
    """View for reverting data table content."""
    datatable = AssessTable(model,"proposed")
    datatable.revert_proposed()
    context = datatable.render_table_context("",False,[])
    return AssessRender(request, 'table_display.html', context, app_name)


def ItemIndexView(request):
    """View for listing all item models."""
    return AssessRender(request, 'item_index.html', {}, 'items')


def ItemListView(request, model, app_name):
    """Render table with all current items."""
    item_set = AssessSet(model)
    context = item_set.get_context()
    return AssessRender(request, 'item_list.html', context, app_name)


def ItemDeleteView(request, pk, model, app_name):
    """Returns views for deleting items."""
    item_set = AssessSet(model)
    item_id = int(pk)
    if request.method == 'GET':
        context = item_set.get_delete_form_context(item_id)
        return AssessRender(request, 'item_delete_form.html', context, app_name)
    elif request.method == 'POST':
        context = item_set.delete(request.POST['id'])
        return AssessRender(request, 'item_list.html', context, app_name)
    else:
        context = item_set.get_context()
        return AssessRender(request, 'item_list.html', context, app_name)


def ItemUpdateView(request, pk, model, app_name):
    """Returns views for updating item name"""
    item_set = AssessSet(model)
    item_id = int(pk)
    if request.method == 'GET':
        context = item_set.get_update_form(item_id)
        return AssessRender(request, 'item_update_form.html', context, app_name)
    elif request.method == 'POST':
        context = item_set.update(request.POST)
        return AssessRender(request, 'item_list.html', context, app_name)
    else:
        context = item_set.get_context()
        return AssessRender(request, 'item_list.html', context, app_name)


def ItemCreateView(request, model, app_name):
    """Return views for creating new items"""
    item_set = AssessSet(model)
    if request.method == 'GET':
        context = item_set.get_create_form_context()
        return AssessRender(request, 'item_create_form.html', context, app_name)
    elif request.method == 'POST':
        context = item_set.create(request.POST['label'])
        return AssessRender(request, 'item_list.html', context, app_name)
    else:
        context = item_set.get_context()
        return AssessRender(request, 'item_list.html', context, app_name)


def ItemUploadView(request, model, app_name):
    """Return views for posting CSV string multiple items."""
    item_set = AssessSet(model)
    if request.method == 'GET':
        context = item_set.get_context()
        return AssessRender(request, 'item_upload_form.html', context, app_name)
    elif request.method == 'POST':
        context = item_set.upload_csv(request.POST['CSVstring'])
        return AssessRender(request, 'item_list.html', context, app_name)
    else:
        return AssessRender(request, 'item_list.html', context, app_name)

