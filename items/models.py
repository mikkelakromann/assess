from base.models import ItemModel

# All  your tables (in Django they are named models) below
# Initiate them by calling "class YourTableName(ItemModel):


class Fraction(ItemModel):
    fields  = [ 'label' ]
        
class Stream(ItemModel):
    fields  = [ 'label' ]

class Generator(ItemModel):
    fields  = [ 'label' ]

class Container(ItemModel):
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
    