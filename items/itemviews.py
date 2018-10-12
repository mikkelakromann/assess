# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:10:24 2018

@author: MIKR
"""

from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.apps import apps
from django.urls import reverse

from . models import GetItemNames
from assess.csv import csv_to_django_model

# The value of the dictionary is used for displaying the name of the model, so call it something human readable
def GetItemDictionary(request):
    d1 = [ ] 
    for i in GetItemNames():
        d1.append( { 'name': i.lower(), 'readable': i, 'urlname': i.lower() + '_list' } )
    return { 'itemDictionary': d1 }

def index(View):
    return ""

########################
# DeleteView
########################
class ItemDeleteView(DeleteView):
    model_name = None
    
    def dispatch(self, request, *args, **kwargs):
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemDeleteView, self).dispatch(request, *args, **kwargs)


########################
# UpdateView
########################

class ItemUpdateView(UpdateView):
    fields = None
    template_name = "item_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemUpdateView, self).dispatch(request, *args, **kwargs)

########################
# CreateView
########################

class ItemCreateView(CreateView):
    fields = None
    template_name = "item_form.html"

# Add the Model's fields to this object
    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        self.model_name = self.model._meta.object_name.lower()
        self.success_url = reverse(self.model_name + "_list")
        return super(ItemCreateView, self).dispatch(request, *args, **kwargs)

########################
# ListView
########################

class ItemListView(ListView):
    fields = None
    template_name = "item_list.html"
   
# Add the Model's field list, and also provide the Model's object_list as a copy named row_list
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_list'] = self.model.fields
        context['row_list'] = self.object_list
        context['model_name'] = self.model._meta.object_name.lower()
        return context

########################
# DetailView
########################

class ItemDetailView(DetailView):
    fields = None
    template_name = "item_detail.html"

# Add the Model's fields to this object
    def dispatch(self, request, *args, **kwargs):
        self.fields = self.model.fields
        return super(ItemDetailView, self).dispatch(request, *args, **kwargs)

########################
# UploadView
########################

def ItemUploadView(request, item_name):
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
        csv = csv_to_django_model(request.POST['csvtable'],Item,delimiters)
        error_message = csv.save_to_database()
        context['row_list'] = csv.rows 
        context['field_list'] = csv.fields
        context['model_name'] = item_name
        context['error_message'] = error_message
        return render(request, 'item_upload_result.html', context )
    else:
        Http404("Invalid HTTP method.")
