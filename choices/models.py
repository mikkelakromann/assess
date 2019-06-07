from django.db import models
from base.models import ItemModel, DataModel, MappingsModel
from items.models import Fraction, Generator, Stream, Location

# Create your models here.

class SystemChoice(ItemModel):
    """User choices for SortingSystem"""
    fields = ['label']

class Development(ItemModel):
    """User choices for development."""
    fields = ['label']


class SortingSystem(DataModel):
    """Share of waste sorted correctly to stream, %"""

    index_fields  = ['systemchoice', 'generator','fraction','stream' ]
    column_field= 'stream'
    value_field = 'value'
    
    systemchoice= models.ForeignKey(SystemChoice,   on_delete=models.CASCADE)
    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    stream      = models.ForeignKey(Stream,         on_delete=models.CASCADE)
    value       = models.DecimalField(max_digits=5, decimal_places=3)


class LocationSystemChoice(MappingsModel):
    """Choice of sorting system by location."""

    index_fields  = ['location' ]
    column_field= 'systemchoice'
    value_field = 'systemchoice'

    location = models.ForeignKey(Location,          on_delete=models.CASCADE)
    systemchoice= models.ForeignKey(SystemChoice,   on_delete=models.CASCADE)


class SortingDevelopment(MappingsModel):
    """Choice for development in sorting efficiency."""

    index_fields  = ['generator', 'fraction', 'stream' ]
    column_field= 'stream'
    value_field = 'development'

    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    stream      = models.ForeignKey(Stream,         on_delete=models.CASCADE)
    development = models.ForeignKey(Development,    on_delete=models.CASCADE)