from django.shortcuts import render
from django.apps import apps


def BaseIndexView(request):
    return render(request, 'base_index.html')

def get_model_name_dicts(app_name,suffix):
    """Return side bar nagivation context dictionary of model names and url names in app_name."""
    links = [ ] 
    for m in apps.get_app_config(app_name).get_models():
        n = m.__name__
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + suffix } )
    return links

def get_top_bar_links(app_name):
    """Return top bar nagivation context as dictionary of model names and url names in app_name."""
    links = [ ]
    for n in ['Items', 'Data', 'Choices', 'Scenarios', 'Results' ]:
        links.append( { 'name': n.lower(), 'readable': n, 'urlname': n.lower() + '_index' } )
    return links    


def get_navigation_links(app_name,suffix):
    context = {}
    context['sidebar_links'] = get_model_name_dicts(app_name,suffix)
    context['topbar_links'] = get_top_bar_links(app_name)
    return context