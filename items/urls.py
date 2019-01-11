from django.urls import path
from django.apps import apps

from . views import ItemIndexView, ItemListView, ItemCreateView, ItemUpdateView, ItemDeleteView, ItemUploadView


def get_item_paths():
    """
    Produce set of url pattern paths for each model in the data app.
    """
    
    paths = [ ]
    for m in apps.get_app_config('items').get_models():
        n = m.__name__
        nL = n.lower()
        paths.append(path( 'list/'+nL+'/' ,         ItemListView.as_view(model=m),      name=nL+'_list'   ) )
        paths.append(path( 'create/'+nL+'/',        ItemCreateView.as_view(model=m),    name=nL+'_create' ) )
        paths.append(path( 'update/'+nL+'/<pk>/',   ItemUpdateView.as_view(model=m),    name=nL+'_update' ) )
        paths.append(path( 'delete/'+nL+'/<pk>/',   ItemDeleteView.as_view(model=m),    name=nL+'_delete' ) )
        paths.append(path( 'upload/'+nL+'/',        ItemUploadView,  {'item_name': n},  name=nL+'_upload' ) )
    return paths

urlpatterns = [ 
        path( '' ,                      ItemIndexView,                        name='item_index' ) ,
        path( 'index' ,                 ItemIndexView,                        name='item_index' ) ,
        path( 'index/' ,                ItemIndexView,                        name='item_index' ) ,
] + get_item_paths()
