from django.db import models
from base.models import DataModel
from items.models import Location, Generator, Fraction, Stream, Container

# Create your models here.

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
    
class SourceSorting(DataModel):
    """Share of waste sorted correctly to stream, %"""
    row_fields  = ['generator','fraction','stream','container' ]
    column_field= 'generator'
    value_field = ['value']
    fields      = ['generator','fraction','stream','container', 'value' ]
    generator   = models.ForeignKey(Generator,      on_delete=models.CASCADE)
    fraction    = models.ForeignKey(Fraction,       on_delete=models.CASCADE)
    stream      = models.ForeignKey(Stream,         on_delete=models.CASCADE)
    container   = models.ForeignKey(Container,      on_delete=models.CASCADE)
    value       = models.DecimalField(max_digits=5, decimal_places=3)
    