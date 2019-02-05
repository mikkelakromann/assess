from django.urls import path
from django.apps import apps

from base.views import TableRevertView
from items.views import ItemCreateView, ItemDeleteView, ItemUpdateView
from . views import ChoicesIndexView, ChoicesDisplayView, ChoicesUploadView, ChoicesCommitView


def get_choices_paths():
    """
    Produce set of url pattern paths for each model in the choices app.
    """
    
    paths = [ ]
    for m in apps.get_app_config('choices').get_models():
        m.model_name = m._meta.object_name.lower()
        m.app_name = 'choices'
        n = m.__name__
        nL = n.lower()
        kwargs = { }
        kwargs['model'] = m

        paths.append(path( nL+'/create/',               ItemCreateView,     kwargs.copy(), name=nL+'_create'  ) )
        paths.append(path( nL+'/update/<pk>/',          ItemUpdateView,     kwargs.copy(), name=nL+'_update'  ) )
        paths.append(path( nL+'/delete/<pk>/',          ItemDeleteView,     kwargs.copy(), name=nL+'_delete'  ) )
        paths.append(path( nL+'/commit/',               ChoicesCommitView,  kwargs.copy(), name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               TableRevertView,    kwargs.copy(), name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               ChoicesUploadView,  kwargs.copy(), name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      ChoicesDisplayView, kwargs.copy(), name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            ChoicesDisplayView, kwargs.copy(), name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  ChoicesDisplayView, kwargs.copy(), name=nL+'_version' ) )
        kwargs['dif'] = True
        paths.append(path( nL+'/<str:ver>/change/',     ChoicesDisplayView, kwargs.copy(), name=nL+'_change' ) )

    return paths


urlpatterns = [
    path( 'index',         ChoicesIndexView,     name='choices_index' ),
] + get_choices_paths()