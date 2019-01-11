from django.shortcuts import render
from base.views import get_model_name_dicts

# Create your views here.


def ChoicesIndexView(request):
    """
    Present list of Choice tables with links and descriptions.
    """
    
    context = { }
    context['model_names'] = get_model_name_dicts('choices','_table')
    return render(request, 'choices_index.html', context )


