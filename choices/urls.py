from django.urls import path
from django.apps import apps

from base.views import TableDisplayView, TableUploadView, TableCommitView, TableRevertView
from . views import ChoicesIndexView, ChoicesDisplayView


def get_choices_paths():
    """
    Produce set of url pattern paths for each model in the choices app.
    """
    
    paths = [ ]
    for m in apps.get_app_config('choices').get_models():
        n = m.__name__
        nL = n.lower()
        kwargs = { }
        kwargs['model'] = m
        kwargs['app_name'] = 'choices' 
        paths.append(path( nL+'/commit/',               TableCommitView,    kwargs.copy(), name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               TableRevertView,    kwargs.copy(), name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               TableUploadView,    kwargs.copy(), name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      ChoicesDisplayView, kwargs.copy(), name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            ChoicesDisplayView, kwargs.copy(), name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  ChoicesDisplayView, kwargs.copy(), name=nL+'_version' ) )
        kwargs['dif'] = True
        paths.append(path( nL+'/<str:ver>/change/',     ChoicesDisplayView,  kwargs, name=nL+'_change' ) )

    return paths


urlpatterns = [
    path( 'index',         ChoicesIndexView,     name='choices_index' ),
] + get_choices_paths()