from .models import MyModel
from django.contrib import admin


admin.site.register(MyModel)

admin.site.site_header = "Administration Panel"
admin.site.site_title = "Object Detection"
admin.site.index_title = "Welcome to Object Detection Portal"
