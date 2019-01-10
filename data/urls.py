from django.urls import path
from django.apps import apps

from . views import DataIndexView, DataTableView, DataUploadView, DataCommitView, DataRevertView


def get_data_paths():
    paths = [ ]
    for m in apps.get_app_config('data').get_models():
        n = m.__name__
        nL = n.lower()
        kwargs = { 'model': m, 'app_name': 'data' }
        paths.append(path( nL+'/commit/',               DataCommitView, kwargs, name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               DataRevertView, kwargs, name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               DataUploadView, kwargs, name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      DataTableView,  kwargs, name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            DataTableView,  kwargs, name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  DataTableView,  kwargs, name=nL+'_version' ) )
        kwargs['dif'] = True
        paths.append(path( nL+'/<str:ver>/change/',     DataTableView,  kwargs, name=nL+'_change' ) )
    return paths

urlpatterns = [
    path( 'index',         DataIndexView,     name='data_index' ),
] + get_data_paths()
