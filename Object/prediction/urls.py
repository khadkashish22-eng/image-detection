from . import views
from django.urls import path


urlpatterns = [
    path("", views.addpredict, name="addpredict"),
    path("predictionhistory", views.prediction_history, name="prediction_history"),
    path(
        "delete/<int:prediction_id>/", views.delete_prediction, name="delete_prediction"
    ),
    path("export-pdf/", views.export_pdf, name="export_pdf"),
]
