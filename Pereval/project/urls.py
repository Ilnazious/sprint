from django.urls import path
from . import views

urlpatterns = [
    path('submitData/', views.SubmitDataView.as_view(), name='submit-data'),
    path('mountain-passes/<int:pk>/', views.MountainPassDetailView.as_view(), name='mountain-pass-detail'),
]