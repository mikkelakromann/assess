from django.urls import path
from . models import GetItemNames
from . itemviews import ItemListView, ItemCreateView, ItemUpdateView, ItemDeleteView, ItemUploadView
from django.apps import apps

def GetItemPaths():
    paths = [ ]
    for i in GetItemNames():
        iL = i.lower()
        m = apps.get_model('items', i)
        paths.append(path( 'list/'+iL+'/' ,         ItemListView.as_view(model=m),      name=iL+'_list'   ) )
        paths.append(path( 'create/'+iL+'/',        ItemCreateView.as_view(model=m),    name=iL+'_create' ) )
        paths.append(path( 'update/'+iL+'/<pk>/',   ItemUpdateView.as_view(model=m),    name=iL+'_update' ) )
        paths.append(path( 'delete/'+iL+'/<pk>/',   ItemDeleteView.as_view(model=m),    name=iL+'_delete' ) )
        paths.append(path( 'upload/'+iL+'/',        ItemUploadView,  {'item_name': i},  name=iL+'_upload' ) )

    return paths

urlpatterns = GetItemPaths() + [

] 
