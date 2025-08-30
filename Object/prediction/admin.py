from .models import Prediction
from django.contrib import admin


# Register your models here.


class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submitted_by",
        "image_file",
        "class_1",
        "prob_1",
        "class_2",
        "prob_2",
        "class_3",
        "prob_3",
    )
    list_display_links = ("id", "submitted_by")
    search_fields = (
        "id",
        "submitted_by",
        "image_file",
        "class_1",
        "prob_1",
        "class_2",
        "prob_2",
        "class_3",
        "prob_3",
    )
    list_per_page = 5


admin.site.register(Prediction, PredictionAdmin)
