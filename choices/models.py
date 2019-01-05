from django.db import models
from base.models import DataModel
from items.models import Fraction, Generator, Stream

# Create your models here.

def GetChoicesNames():
    """Returns a list of all item names in the application"""
    return [ SortingSystem, ] 

class SortingSystem(DataModel):
    """Share of waste sorted correctly to stream, %"""
    row_fields  = ['generator','fraction','stream','container' ]
    column_field= 'generator'
    value_field = ['value']
    fields      = ['generator','fraction','stream', 'value' ]
    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    stream      = models.ForeignKey(Stream,         on_delete=models.CASCADE)
    value       = models.DecimalField(max_digits=5, decimal_places=3)
