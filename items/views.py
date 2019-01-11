from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.apps import apps
from django.urls import reverse

from base.views import get_navigation_links


def ItemIndexView(request):
    """
    View for listing all item models.
    """
    context = get_navigation_links("items","_list")
    return render(request, 'item_index.html', context )


class ItemDeleteView(DeleteView):
    """
    Class Based View for deleting an item.
    """
    model_name = None
    
    def dispatch(self, request, *args, **kwargs):
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemDeleteView, self).dispatch(request, *args, **kwargs)


class ItemUpdateView(UpdateView):
    """
    Class Based View for updating an item.
    """
    fields = None
    template_name = "item_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemUpdateView, self).dispatch(request, *args, **kwargs)


class ItemCreateView(CreateView):
    """
    Class Based View for creating an item.
    """
    
    fields = None
    template_name = "item_form.html"

# Modify dispatch() to add the Model's fields to this object
    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemCreateView, self).dispatch(request, *args, **kwargs)


class ItemListView(ListView):
    """
    Class Based View for listing all items.
    """
    
    fields = None
    template_name = "item_list.html"
   
    # Add the Model's field list, and also provide the Model's 
    # object_list as a copy named row_list
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_list'] = self.model.fields
        context['row_list'] = self.object_list
        context['model_name'] = self.model._meta.object_name.lower()
        context.update(get_navigation_links("items","_list"))
        return context


class ItemDetailView(DetailView):
    """
    Class Based View for viewing items details.
    """
    
    fields = None
    template_name = "item_detail.html"

    # Add the Model's fields to this object
    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        return super(ItemDetailView, self).dispatch(request, *args, **kwargs)


def ItemUploadView(request, item_name):
    """
    View for posting CSV string multiple items.
    """

    error_message = ""
    context = { }
    try:
        Item = apps.get_model('items',item_name)
    except:
        Http404("Table " + item_name + "does not exist!")
    if request.method == 'GET':
        return render(request, 'item_upload_form.html', {'item_name': item_name.lower })
    elif request.method == 'POST':
        delimiters = {'decimal': ',', 'thousand': '.' }
        csv = csv_to_list_of_dicts(request.POST['csvtable'],Item,delimiters)
        Item.import_rows(csv.rows)
        context['row_list'] = csv.rows 
        context['field_list'] = csv.fields
        context['model_name'] = item_name
        context['error_message'] = error_message
        return render(request, 'item_upload_result.html', context )
    else:
        Http404("Invalid HTTP method.")
