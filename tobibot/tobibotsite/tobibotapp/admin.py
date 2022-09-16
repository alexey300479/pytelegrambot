from django.contrib import admin
from . import models


class ResidentAdmin(admin.ModelAdmin):
    # list_display = ('first_name', 'last_name')
    # readonly_fields = ['photo']

    def photo_preview(self, obj):
        return obj.photo_preview

    photo_preview.short_description = 'Предпросмотр фото'
    photo_preview.allow_tags = True


# Register your models here.
admin.site.register(models.Branch)
admin.site.register(models.Resident, ResidentAdmin)
admin.site.register(models.Building)
