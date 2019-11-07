from django.urls import path
from . views import BaseIndexView

urlpatterns = [ path('', BaseIndexView, name='base_index') ]


