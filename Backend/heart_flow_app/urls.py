from django.urls import path
from . views import *

urlpatterns = [
    path('patient-registration/',PatientRegisterView.as_view(),name='pateint-registration'),
    path('user-login/',UserLoginAPIView.as_view(),name='user-login'),
    path('verify-otp/',VerifyOTPView.as_view(),name='verify-otp'),
    path('cardiologist-registration/',CardiologistRegisterView.as_view(),name='cardiologist-registration'),
    
]