from base.models import ItemModel

# You MUST fill out the GetItemNames list with all your items in the application
def GetItemNames():
    """Returns a list of all item names in the application"""
    return [ 'Fraction', 'Stream', 'Generator', 'Year', 'Vintage', 'Region', 'Location', 'Plant', 'Truck' ] 

# All  your tables (in Django they are named models) below
# Initiate them by calling "class YourTableName(ItemModel):
# You MUST fill out the "fields" list with the names of all the data columns you want the user to have access to


class Fraction(ItemModel):
    fields  = [ 'label' ]
        
class Stream(ItemModel):
    fields  = [ 'label' ]

class Generator(ItemModel):
    fields  = [ 'label' ]
        
class Region(ItemModel):
    fields  = [ 'label' ]

class Location(ItemModel):
    fields  = [ 'label' ]

class Year(ItemModel):
    fields  = [ 'label' ]

class Vintage(ItemModel):
    fields  = [ 'label' ]

class Plant(ItemModel):
    fields  = [ 'label' ]
    
class Truck(ItemModel):
    fields  = [ 'label' ]
    