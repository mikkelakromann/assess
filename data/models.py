from django.db import models
from base.models import DataModel
from items.models import Location, Generator, Fraction

# Create your models here.

def GetDataNames():
    """Returns a list of all item names in the application"""
    return [ 'Generation' ] 


def get_UNIT_CHOICES():
    return { ('POP', 'Population'), ('FAM', 'Families') }

class Generation(DataModel):
    """Waste generation, kg/unit/year"""

    row_fields  = ['location', 'generator', 'unit']
    column_field= 'fraction'
    value_field = ['value']
    fields      = ['location', 'generator', 'unit', 'fraction', 'value' ]
    location    = models.ForeignKey(Location,       on_delete=models.CASCADE)
    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    unit        = models.CharField(max_length=3,    choices=get_UNIT_CHOICES())
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    value       = models.DecimalField(max_digits=5, decimal_places=2)