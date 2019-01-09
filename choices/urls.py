from django.urls import path
from django.apps import apps

from data.views import DataIndexView, DataTableView, DataUploadView, DataCommitView, DataRevertView
from . views import ChoicesIndexView

def get_choices_paths():
    paths = [ ]
    for m in apps.get_app_config('choices').get_models():
        n = m.__name__
        nL = n.lower()
        paths.append(path( nL+'/commit/',               DataCommitView, { 'model': m }, name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               DataRevertView, { 'model': m }, name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               DataUploadView, { 'model': m }, name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      DataTableView,  { 'model': m }, name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            DataTableView,  { 'model': m }, name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/change/',     DataTableView,  { 'model': m, 'dif': True }, name=nL+'_change' ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  DataTableView,  { 'model': m }, name=nL+'_version' ) )
    return paths


urlpatterns = [
    path( 'index',         ChoicesIndexView,     name='choices_index' ),
] + get_choices_paths()