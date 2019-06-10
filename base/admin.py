from django.contrib import admin
from base.models import Version, TestItemA, TestItemB, TestItemC, TestData

# Register your models here.
admin.site.register(Version)
admin.site.register(TestItemA)
admin.site.register(TestItemB)
admin.site.register(TestItemC)
admin.site.register(TestData)
