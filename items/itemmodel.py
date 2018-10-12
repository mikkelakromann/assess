# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:05:47 2018

@author: MIKR
"""

from django.db import models

class Version(models.Model):
    label =  models.CharField(max_length=15)
    user =  models.CharField(max_length=15)
    date =   models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

# IDEA: Add "Change label name" as separate action, to ensure that label names remain unique.
#       Remove label from the update form

class ItemModel(models.Model):
    """Abstract class for all our items inkl. point-in-time architecture for table history"""
    fields = [ 'label', 'short', 'descr' ]
    label   = models.CharField(max_length=10)
    short   = models.CharField(max_length=15)
    descr   = models.CharField(max_length=40)
#    id_previous = models.IntegerField(null=True, default=0)
#    version_begin = models.ForeignKey(Version, null=True)
#    version_stop = models.ForeignKey(Version, null=True)
#    version_next = models.ForeignKey(Version, null=True)
                  

# LOGIC OF Point-in-Time-Architecture (PTA) for history of database
# See https://www.red-gate.com/simple-talk/sql/database-administration/database-design-a-point-in-time-architecture/
# PTA never delete or update rows, it is always insert-only
# PTA is described by an start and end version for each record, as well as version (foreign key reference to version table)
# In ItemModel, status of records can be proposed, committed or archived (X and Y designates version foreign keys)
# - proposed: add_version = X, end_version = X (X is current database history version)
# - commited: add_version = X, end_version = null (X is database version at record creation)
# - archived: add_version = X, end_version = Y (X is database version at record creation, Y is database version at record ending)
# Actions for the record are:
# - update: id_original != id_previous
# - delete: id_original == id_previous
# - insert: id_original == id
# On proposed INSERT: insert record, set add_version = end_version = [current version]
# On commited INSERT: update record, set add_version = [next version]; set end_version = null 
# On proposed DELETE: update record, set add_version = end_version = [current version]
# On commited DELETE: update record, set add_version = [next version]; set end_version = null 
# On proposed UPDATE: insert record, set add_version = end_version = [current version]
# On commited UPDATE: update record, set add_version = [next version]; set end_version = null 

    def __str__(self):
        return self.short

    def get_field_types(self):
        field_types = { }
        for field in self.fields:
            field_types[field] = self._meta.get_field(field).get_internal_type()
        return field_types
        
    def get_id_labels_dict(self):
        """Returns a dictionary of all label/pk pairs for this model."""
        id_labels_dict = { }
        queryset = self.objects.all()
        for query in queryset:
            id_labels_dict[query.label] = query.id
        return id_labels_dict
        
    class Meta:
        abstract = True

