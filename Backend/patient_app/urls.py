from django.urls import path
from . views import *

urlpatterns = [
    path('list-all-patients/',ListPatientsAPIView.as_view(),name='list-patients'),
    path('list-all-doctors/',ListAllCardiologist.as_view(),name='list-all-doctors'),
    path('get-patient-profile/',GetPatientProfileByIDAPIView.as_view(),name='get-patient-profile'),
    path('update-patient-profile/',UpdatePatientProfileAPIView.as_view(),name='update-patient-profile'),
    path('book-appointment/',BookAppointmentAPIView.as_view(),name='book-appointment'),
]