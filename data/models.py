from django.db import models
from base.models import DataModel
from items.models import Location, Generator, Fraction

# Create your models here.

def GetDataNames():
    """Returns a list of all item names in the application"""
    return [ 'Generation' ] 

class Generation(DataModel):
    """Waste generation, kg/unit/year"""

    row_fields  = ['location', 'generator' ]
    column_field= 'fraction'
    value_field = ['value']
    fields      = ['location', 'generator', 'fraction', 'value' ]
    location    = models.ForeignKey(Location,       on_delete=models.CASCADE)
    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    value       = models.DecimalField(max_digits=8, decimal_places=2)