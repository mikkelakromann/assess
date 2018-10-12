from django.db import models
from . itemmodel import ItemModel

# You MUST fill out the GetItemNames list with all your items in the application
def GetItemNames():
    """Returns a list of all item names in the application"""
    return [ 'Year', 'Vintage', 'Region', 'Location', 'Plants', 'Trucks' ] 

# All  your tables (in Django they are named models) below
# Initiate them by calling "class YourTableName(ItemModel):
# You MUST fill out the "fields" list with the names of all the data columns you want the user to have access to
        
class Region(ItemModel):
    fields  = [ 'label', 'short', 'descr' ]

class Location(ItemModel):
    fields  = [ 'label', 'short', 'descr', 'region' ]
    region  = models.ForeignKey(Region, on_delete=models.CASCADE)

class Year(ItemModel):
    fields  = [ 'label', 'short', 'descr' ]

class Vintage(ItemModel):
    fields  = [ 'label', 'short', 'descr', 'year' ]
    year    = models.ForeignKey(Year, on_delete=models.CASCADE)

class Plants(ItemModel):
    fields  = [ 'label', 'short', 'descr', 'vintage', 'location', 'capex', 'fopex', 'vopex' ]
    vintage = models.ForeignKey(Vintage, on_delete=models.CASCADE)
    location= models.ForeignKey(Location, on_delete=models.CASCADE)
    capex   = models.DecimalField(decimal_places=2, max_digits=4)
    fopex   = models.DecimalField(decimal_places=2, max_digits=4)
    vopex   = models.DecimalField(decimal_places=2, max_digits=4)
    
class Trucks(ItemModel):
    fields  = [ 'label', 'short', 'descr', 'vintage', 'capex', 'fopex', 'vopex'  ]
    vintage = models.ForeignKey(Vintage, on_delete=models.CASCADE)
    capex   = models.DecimalField(decimal_places=2, max_digits=4)
    fopex   = models.DecimalField(decimal_places=2, max_digits=4)
    vopex   = models.DecimalField(decimal_places=2, max_digits=4)
    