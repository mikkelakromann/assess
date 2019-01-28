from django.contrib import admin

# Register your models here.


from .models import Region, Location, Fraction, Generator

admin.site.register(Region)
admin.site.register(Location)
admin.site.register(Fraction)
admin.site.register(Generator)