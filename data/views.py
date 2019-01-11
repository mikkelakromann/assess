from django.http import Http404
from django.shortcuts import render
from base.views import get_model_name_dicts, get_navigation_links
from base.table import AssessTable


# Create your views here.


def DataIndexView(request):
    """
    Present list of Choice tables with links and descriptions.
    """
    
    context = get_navigation_links('data','_table')
    return render(request, 'data_index.html', context )

