from django.urls import path
from .views import (
    SubmitDataAPIView,
    SubmitDataDetailAPIView,
    SubmitDataListAPIView
)

urlpatterns = [
    path('submitData/', SubmitDataAPIView.as_view(), name='submit-data'),
    path('submitData/<int:pk>/', SubmitDataDetailAPIView.as_view(), name='submit-data-detail'),
    path('submitData/list/', SubmitDataListAPIView.as_view(), name='submit-data-list'),
]