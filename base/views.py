from django.shortcuts import render
from django.apps import apps


def BaseIndexView(request):
    return render(request, 'base_index.html')

def get_model_names(app_name):
    """Return list of names of all models in app_name."""
    return []
    
def get_model_name_dicts(app_name,suffix):
    """Return dictionary of model names and url names in app_name"""
    models = [ ] 
    for m in apps.get_app_config(app_name).get_models():
        print(m)
        n = m.__name__
        models.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + suffix } )
    return models


def get_navigation_links(app_name,suffix):
    context = {}
    context['sidebar_links'] = get_model_name_dicts(app_name,suffix)
    context['topbar_links'] = []
    return context