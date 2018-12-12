# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 08:54:51 2018

@author: MIKR
"""
from base.models import Version


class History():
    """Account for the history of the model so far.
    Provide information and functionality for viewing model history.
    The history of the table derived from data saved when a version 
    is committed. There is (so far) no check on whether saved history 
    matches the actual table."""
    
    def __init__(self,model):
        self.model = model
        self.model_name = self.model._meta.object_name.lower()
        self.context_data = [ ] 

        proposed = Version()
        proposed.cells = model.get_cells(model,None)
        if proposed.cells >0:
            proposed.size = model.get_size(model)
            proposed.changes = proposed.cells
            proposed.dimension = model.get_dimension(model)
            proposed.metric = model.get_metric(model)
            proposed.status = "Proposed"
            proposed.version_link = self.model_name + "_version"
            proposed.commit_link = self.model_name + "_commit"
            proposed.revert_link = self.model_name + "_revert"
            self.context_data.append(proposed)
#        for version in Version.objects.filter('model_name'=self.model_name).order_by('-version_first'):
#        versions = Version.objects.order_by('-version_first')
        versions = Version.objects.all()
        for version in versions:
            print(version)
            version.status = "Archived"
            version.version_link = self.model_name + "_version"
            self.context_data.append(version)
        

