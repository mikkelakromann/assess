from django.db import models
from base.models import ItemModel, DataModel
from items.models import Fraction, Generator, Stream

# Create your models here.

class SortingSystemChoices(ItemModel):
    """User choices for SortingSystem"""
    fields = ['label']

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
