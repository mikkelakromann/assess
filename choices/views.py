from django.shortcuts import render
from django.http import Http404

from base.views import get_model_name_dicts, get_top_bar_links
from base.table import AssessTable

# Create your views here.


def ChoicesIndexView(request):
    """
    Present list of Choice tables with links and descriptions.
    """
    
    context = { }
    context['item_links'] = get_model_name_dicts('choices','_table','item_model')
    context['data_links'] = get_model_name_dicts('choices','_table','data_model')
    context['topbar_links'] = get_top_bar_links('choices')
    return render(request, 'choices_index.html', context )


def ChoicesDisplayView(request,model,col="",ver="",dif=""):
    """
    View for displaying data table content.
    """

    context = { }
    context['item_links'] = get_model_name_dicts('choices','_table','item_model')
    context['data_links'] = get_model_name_dicts('choices','_table','data_model')
    context['topbar_links'] = get_top_bar_links('choices')

    if model.model_type == 'data_model':
        datatable = AssessTable(model)
        datatable.load_model(ver,dif)
        datatable.pivot_1dim(col)
        context.update(datatable.get_context('data'))
    elif model.model_type == 'item_model':
        context.update(model.get_current_list_context(model))
        print(context)
    else:
        Http404("Invalid data model type.")
    return render(request, 'choices_table.html', context)


def ChoicesUploadView(request,model):
    """
    View for uploading data table content.
    """

    context = { }
    context['model_name'] = model.model_name 
    context['item_links'] = get_model_name_dicts('choices','_table','item_model')
    context['data_links'] = get_model_name_dicts('choices','_table','data_model')
    context['topbar_links'] = get_top_bar_links('choices')

    # Choices can be either data_model or item_model
    # data_models are handled by the class datatable (copied from data/views.py)
    if model.model_type == 'data_model':
        if request.method == 'GET':
            return render(request, 'data_upload_form.html', context )
        elif request.method == 'POST':
            delimiters = {'decimal': ',', 'thousands': '.', 'sep': '\t' }
            datatable = AssessTable(model)
            datatable.load_csv(request.POST['csv_string'],delimiters)
            datatable.save_dataframe()
            datatable.load_model("proposed")
            datatable.pivot_1dim("")
            context.update(datatable.get_context('data'))
            return render(request, 'choices_table.html', context)
        else:
            Http404("Invalid HTTP method.")
    # item_models are handled by the item class (copied from data/views.py)
    elif model.model_type == 'item_model':
        if request.method == 'GET':
            return render(request, 'item_upload_form.html', context )
        elif request.method == 'POST':
            CSVstring = request.POST['CSVstring']
            context['message'] = model.upload(model,CSVstring)
            context.update(model.get_current_list_context(model))
            return render(request, 'choices_table.html', context )
        else:
            context.update(model.get_current_list_context(model))
            return render(request, 'item_list.html', context )
    else:
        Http404("Invalid data model type.")


def ChoicesCommitView(request,model):
    """
    View for committing choices table content.
    """

    model_name = model._meta.object_name.lower()
    datatable = AssessTable(model)

    context = { }
    context['model_name'] = model.model_name 
    context['item_links'] = get_model_name_dicts('choices','_table','item_model')
    context['data_links'] = get_model_name_dicts('choices','_table','data_model')
    context['topbar_links'] = get_top_bar_links('choices')

    # Do not enter commit branch if there is nothing to commit
    if datatable.proposed_count() == 0:
        context['nothing_proposed'] = "There was nothing to commit in table " + model_name + "."
        datatable.load_model("current")
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
            datatable.load_model("current")
            datatable.pivot_1dim("")
            context.update(datatable.get_context('data'))
            return render(request, 'data_table.html', context)
