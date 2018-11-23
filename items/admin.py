from django.contrib import admin

# Register your models here.


from .models import Region, Location, Generator

admin.site.register(Region)
admin.site.register(Location)
admin.site.register(Generator)