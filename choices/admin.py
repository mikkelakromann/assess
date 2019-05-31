from django.contrib import admin

from . models import SystemChoice, LocationSystemChoice, SortingSystem

# Register your models here.
admin.site.register(SystemChoice)
admin.site.register(LocationSystemChoice)
admin.site.register(SortingSystem)