# document_processor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("fetch-raw/", views.FetchRawView.as_view(), name="fetch-raw"),
    path("fetch-clean/", views.CleanDataView.as_view(), name="fetch-clean"),
    path("submit-clean/", views.SubmitCleanView.as_view(), name="submit-clean"),
]