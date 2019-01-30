from django.shortcuts import render

from base.views import get_navigation_links
from base.messages import Messages


def ItemIndexView(request):
    """
    View for listing all item models.
    """

    context = get_navigation_links("items","_list",['item_model'])
    return render(request, 'item_index.html', context )


def ItemListView(request, model):
    """
    Render table with all current items
    """

    model.model_name = model._meta.object_name.lower()
    context = { }
    context.update(get_navigation_links("items","_list",['item_model']))
    context.update(model.get_current_list_context(model))
    context['model_name'] = model.model_name
    return render(request, 'item_list.html', context )


def ItemDeleteView(request, pk, model):
    """
    Returns views for deleting items.
    """
    
    context = get_navigation_links("items","_list",['item_model'])
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


def ItemUpdateView(request, pk, model):
    """
    Returns views for updating item name
    """
    
    context = get_navigation_links("items","_list",['item_model'])
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
    

def ItemCreateView(request, model):
    """
    Return views for creating new items
    """

    context = get_navigation_links("items","_list",['item_model'])
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


def ItemUploadView(request, model):
    """
    Return views for posting CSV string multiple items.
    """
    
    context = get_navigation_links("items","_list",['item_model'])
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

