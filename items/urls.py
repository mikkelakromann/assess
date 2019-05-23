from base.views import get_url_paths

urlpatterns = get_url_paths('items')


#from django.urls import path
#from django.apps import apps
#
#from base.views import ItemIndexView, ItemListView, ItemCreateView, ItemUpdateView, ItemDeleteView, ItemUploadView
#
#
#def get_item_paths():
#    """
#    Produce set of url pattern paths for each model in the data app.
#    """
#    
#    paths = [ ]
#    for m in apps.get_app_config('items').get_models():
#        n = m.__name__
#        nL = n.lower()
#        paths.append(path( 'list/'+nL+'/' ,         ItemListView,   { 'model': m }, name=nL+'_list'   ) )
#        paths.append(path( 'create/'+nL+'/',        ItemCreateView, { 'model': m }, name=nL+'_create' ) )
#        paths.append(path( 'update/'+nL+'/<pk>/',   ItemUpdateView, { 'model': m }, name=nL+'_update' ) )
#        paths.append(path( 'delete/'+nL+'/<pk>/',   ItemDeleteView, { 'model': m }, name=nL+'_delete' ) )
#        paths.append(path( 'upload/'+nL+'/',        ItemUploadView, { 'model': m }, name=nL+'_upload' ) )
#    return paths
#
#urlpatterns = [ 
#        path( '' ,                      ItemIndexView,                        name='item_index' ) ,
#        path( 'index' ,                 ItemIndexView,                        name='item_index' ) ,
#        path( 'index/' ,                ItemIndexView,                        name='item_index' ) ,
#] + get_item_paths()
