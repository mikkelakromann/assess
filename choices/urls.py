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
#        kwargs = { }
#        kwargs['model'] = m

        kwargs1 = { 'model': m,  'dif': False }
        kwargs2 = { 'model': m,  'dif': True  }

        paths.append(path( nL+'/create/',               ItemCreateView,     kwargs1, name=nL+'_create'  ) )
        paths.append(path( nL+'/update/<pk>/',          ItemUpdateView,     kwargs1, name=nL+'_update'  ) )
        paths.append(path( nL+'/delete/<pk>/',          ItemDeleteView,     kwargs1, name=nL+'_delete'  ) )
        paths.append(path( nL+'/commit/',               ChoicesCommitView,  kwargs1, name=nL+'_commit'  ) )
        paths.append(path( nL+'/revert/',               TableRevertView,    kwargs1, name=nL+'_revert'  ) )
        paths.append(path( nL+'/upload/',               ChoicesUploadView,  kwargs1, name=nL+'_upload'  ) )
        paths.append(path( nL+'/',                      ChoicesDisplayView, kwargs1, name=nL+'_table'   ) )
        paths.append(path( nL+'/<str:ver>/',            ChoicesDisplayView, kwargs1, name=nL+'_version' ) )
        paths.append(path( nL+'/<str:ver>/change/',     ChoicesDisplayView, kwargs2, name=nL+'_change' ) )
        paths.append(path( nL+'/<str:ver>/<str:col>/',  ChoicesDisplayView, kwargs1, name=nL+'_version' ) )

    return paths


urlpatterns = [
    path( 'index',         ChoicesIndexView,     name='choices_index' ),
] + get_choices_paths()