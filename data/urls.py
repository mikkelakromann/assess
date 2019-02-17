from django.urls import path
from django.apps import apps

from .views import DataIndexView
from base.views import TableDisplayView, TableUploadView, TableCommitView, TableRevertView


def get_data_paths():
    """
    Produce set of url pattern paths for each model in the data app.
    """
    
    paths = [ ]
    for m in apps.get_app_config('data').get_models():
        n = m.__name__
        nL = n.lower()
        kwargs1 = { 'model': m, 'app_name': 'data', 'dif': False }
        kwargs2 = { 'model': m, 'app_name': 'data', 'dif': True  }
        paths.append(path( nL+'/commit/',               TableCommitView,    kwargs1, name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               TableRevertView,    kwargs1, name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               TableUploadView,    kwargs1, name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      TableDisplayView,   kwargs1, name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            TableDisplayView,   kwargs1, name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/change/',     TableDisplayView,   kwargs2, name=nL+'_change'  ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  TableDisplayView,   kwargs1, name=nL+'_version' ) )
    return paths

urlpatterns = [
    path( 'index',         DataIndexView,     name='data_index' ),
] + get_data_paths()
