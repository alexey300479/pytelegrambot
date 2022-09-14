import imp
from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Branch)
admin.site.register(models.Resident)
admin.site.register(models.Building)
