from django.shortcuts import render
from rest_framework.views import APIView 
from heart_flow_app.mixins import *
from heart_flow_app.serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from heart_flow_app. utils import *
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
# Create your views here.


# list all patients api
class ListPatientsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        patients = PatientProfile.objects.all()
        serializer = PatientProfileSerializer(patients, many=True)
        return custom_200(serializer.data)


# list patient profile based on login patient
class GetPatientProfileByIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        patient_id = request.user.id
        patient = PatientProfile.objects.get(id=patient_id)
        serializer = PatientProfileSerializer(patient)
        return custom_200(serializer.data)


# update patient profile api
class UpdatePatientProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self,request):
        patient_id = request.user.id
        patient = PatientProfile.objects.get(id=patient_id)
        serializer = PatientProfileSerializer(patient,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return custom_200("Patient profile updated successfully")
        return custom_404(serializer.errors)


#get the user by login user
class GetUserByLoginUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        serializer = UserSerializer(user)
        return custom_200(serializer.data)


# book appointment api by patient and also by front office staff that is admin staff
class BookAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get patient ID from request data or from the logged-in user
        patient_id = request.data.get('patient_id', request.user.id)

        try:
            patient = PatientProfile.objects.get(id=patient_id)
            appointment_data = request.data.copy()
            appointment_data['patient'] = patient_id

            serializer = BookAppointmentSerializer(data=appointment_data)
            if serializer.is_valid():
                appointment = serializer.save()

                # Get the doctor
                doctor = appointment.doctor

                # Save notifications
                Notification.objects.create(
                    user=patient,
                    appointment=appointment,
                    notification_type='appointment_created',
                    title='Appointment Booked',
                    message=f"Your appointment with Dr. {doctor.get_full_name()} on {appointment.date} at {appointment.time} is confirmed."
                )

                Notification.objects.create(
                    user=doctor,
                    appointment=appointment,
                    notification_type='appointment_created',
                    title='New Appointment',
                    message=f"You have a new appointment with {patient.get_full_name()} on {appointment.date} at {appointment.time}."
                )

                # Send email to patient
                send_email_notification(
                    subject="Your Appointment is Confirmed",
                    message=f"Dear {patient.get_full_name()},\n\nYour appointment with Dr. {doctor.get_full_name()} is scheduled on {appointment.date} at {appointment.time}.",
                    recipient_list=[patient.user.email]
                )

                # Send email to doctor
                send_email_notification(
                    subject="New Appointment Scheduled",
                    message=f"Dear Dr. {doctor.get_full_name()},\n\nYou have a new appointment with {patient.get_full_name()} on {appointment.date} at {appointment.time}.",
                    recipient_list=[doctor.user.email]
                )

                return custom_200("Appointment booked successfully")

            return custom_404(serializer.errors)

        except PatientProfile.DoesNotExist:
            return custom_404("Patient not found")