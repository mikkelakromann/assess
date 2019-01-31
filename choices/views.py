from django.shortcuts import render
from base.views import get_navigation_links
from base.table import AssessTable

# Create your views here.


def ChoicesIndexView(request):
    """
    Present list of Choice tables with links and descriptions.
    """
    
    context = { }
    context = get_navigation_links('choices', '_table',['data_model'])
    return render(request, 'choices_index.html', context )


def ChoicesDisplayView(request,model,app_name,col="",ver="",dif=""):
    """
    View for displaying data table content.
    """

    datatable = AssessTable(model)
    datatable.load_model(ver,dif)
    datatable.pivot_1dim(col)
    context = get_navigation_links(app_name, '_table',['data_model'])
    context.update(datatable.get_context('data'))
    return render(request, 'choices_table.html', context)
