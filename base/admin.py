from django.contrib import admin
from base.models import Version, TestItemA, TestItemB, TestItemC, TestData, TestMappings

# Register your models here.
admin.site.register(Version)
admin.site.register(TestItemA)
admin.site.register(TestItemB)
admin.site.register(TestItemC)
admin.site.register(TestData)
admin.site.register(TestMappings)