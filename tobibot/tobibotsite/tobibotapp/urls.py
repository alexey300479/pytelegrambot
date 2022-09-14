import imp
from pkgutil import ImpImporter
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
