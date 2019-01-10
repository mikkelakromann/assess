from django.urls import path
from django.apps import apps

from data.views import DataIndexView, DataTableView, DataUploadView, DataCommitView, DataRevertView
from . views import ChoicesIndexView

def get_choices_paths():
    """Produce set of url pattern paths for each model in the choices app."""
    paths = [ ]
    for m in apps.get_app_config('choices').get_models():
        n = m.__name__
        nL = n.lower()
        kwargs = { 'model': m, 'app_name': 'choices' }
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
    path( 'index',         ChoicesIndexView,     name='choices_index' ),
] + get_choices_paths()