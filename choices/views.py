from django.shortcuts import render
from base.views import get_model_name_dicts
from base.table import AssessTable

# Create your views here.


def ChoicesIndexView(request):
    context = { }
    context['model_names'] = get_model_name_dicts('choices','_table')
    return render(request, 'choices_index.html', context )


########################
# TableView
########################

def ChoicesTableView(request,model,col="",ver="",dif=""):
    choicestable = AssessTable(model)
    choicestable.load_model(ver,dif)
    choicestable.pivot_1dim(col)
    return render(request, 'choices_table.html', choicestable.get_context('choices'))
