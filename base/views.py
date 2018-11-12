from django.shortcuts import render

def BaseIndexView(request):
    return render(request, 'base_index.html')