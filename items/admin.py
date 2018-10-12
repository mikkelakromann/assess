from django.contrib import admin

# Register your models here.


from .models import Region, Location

admin.site.register(Region)
admin.site.register(Location)