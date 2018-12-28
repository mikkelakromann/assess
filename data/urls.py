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
        paths.append(path( dL+'/commit/',               DataCommitView, { 'model': m }, name=dL+'_commit'  ) )
        paths.append(path( dL+'/revert/',               DataRevertView, { 'model': m }, name=dL+'_revert'  ) )
        paths.append(path( dL+'/upload/',               DataUploadView, { 'model': m }, name=dL+'_upload'  ) )
        paths.append(path( dL+'/',                      DataTableView,  { 'model': m }, name=dL+'_table'   ) )
        paths.append(path( dL+'/<str:ver>/',            DataTableView,  { 'model': m }, name=dL+'_version' ) )
        paths.append(path( dL+'/<str:ver>/change/',     DataTableView,  { 'model': m, 'dif': True }, name=dL+'_change' ) )
        paths.append(path( dL+'/<str:ver>/<str:col>/',  DataTableView,  { 'model': m }, name=dL+'_version' ) )
#        paths.append(path( dL+'/pivot/<str:col>/',      DataTableView,  { 'model': m }, name=dL+'_table1D' ) )
    return paths

urlpatterns = [
    path( 'index',         DataIndexView,     name='data_index' ),
] + GetDataPaths()
