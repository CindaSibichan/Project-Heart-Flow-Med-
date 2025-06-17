from django.urls import path
from . views import *

urlpatterns = [
    path('list-patients/',ListPatientsAPIView.as_view(),name='list-patients'),
    path('get-patient-profile/',GetPatientProfileByIDAPIView.as_view(),name='get-patient-profile'),
    path('update-patient-profile/',UpdatePatientProfileAPIView.as_view(),name='update-patient-profile'),
]