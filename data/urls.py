# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 08:46:39 2018

@author: MIKR
"""

from django.urls import path
from . models import GetDataNames
from . views import DataIndexView, DataTableView, DataUploadView, DataCommitView, DataRevertView
from django.apps import apps

def GetDataPaths():
    paths = [ ]
    for d in GetDataNames():
        dL = d.lower()
        m = apps.get_model('data', d)
        paths.append(path( 'commit/'+dL+'/',                        DataCommitView, { 'model': m }, name=dL+'_commit'  ) )
        paths.append(path( 'revert/'+dL+'/',                        DataRevertView, { 'model': m }, name=dL+'_revert'  ) )
        paths.append(path( 'upload/'+dL+'/',                        DataUploadView, { 'model': m }, name=dL+'_upload'  ) )
        paths.append(path( 'table/'+dL+'/',                         DataTableView,  { 'model': m }, name=dL+'_table'   ) )
        paths.append(path( 'table/'+dL+'/<str:col>/',               DataTableView,  { 'model': m }, name=dL+'_table1D' ) )
        paths.append(path( 'version/'+dL+'/<str:ver>/',             DataTableView,  { 'model': m }, name=dL+'_version' ) )
        paths.append(path( 'version/'+dL+'/<str:ver>/<str:col>/',   DataTableView,  { 'model': m }, name=dL+'_version' ) )
    return paths

urlpatterns = [
    path( 'index',         DataIndexView,     name='data_index' )
] + GetDataPaths()
