from django.shortcuts import render
from rest_framework.views import APIView 
from heart_flow_app.mixins import *
from heart_flow_app.serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from heart_flow_app. utils import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
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
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            # Get the patient profile using the user ID from the token
            patient = PatientProfile.objects.get(user=request.user)
            serializer = PatientProfileSerializer(patient)
            
            # Format the response data
            response_data = {
                "id": serializer.data["id"],
                "email": serializer.data["user"]["email"],
                "first_name": serializer.data["user"]["first_name"],
                "last_name": serializer.data["user"]["last_name"],
                "role": serializer.data["user"]["role"],
                "is_verified": serializer.data["user"]["is_verified"],
                "date_of_birth": serializer.data["date_of_birth"],
                "gender": serializer.data["gender"],
                "address": serializer.data["address"],
                "emergency_contact": serializer.data["emergency_contact"],
                "insurance_provider": serializer.data["insurance_provider"],
                "insurance_id": serializer.data["insurance_id"],
                "country": serializer.data["country"],
                "unique_id": serializer.data["unique_id"]
            }
            
            return custom_200(response_data)
        except PatientProfile.DoesNotExist:
            return custom_404("Patient profile not found. Please complete your profile registration.")
        except Exception as e:
            return custom_404(f"Error fetching patient profile: {str(e)}")


# update patient profile api
class UpdatePatientProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request):
        try:
            # Get the patient profile using the user from the token
            patient = PatientProfile.objects.get(user=request.user)
            
            # Update the patient profile
            serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Format the response data
                response_data = {
                    "id": serializer.data["id"],
                    "email": serializer.data["user"]["email"],
                    "first_name": serializer.data["user"]["first_name"],
                    "last_name": serializer.data["user"]["last_name"],
                    "role": serializer.data["user"]["role"],
                    "is_verified": serializer.data["user"]["is_verified"],
                    "date_of_birth": serializer.data["date_of_birth"],
                    "gender": serializer.data["gender"],
                    "address": serializer.data["address"],
                    "emergency_contact": serializer.data["emergency_contact"],
                    "insurance_provider": serializer.data["insurance_provider"],
                    "insurance_id": serializer.data["insurance_id"],
                    "country": serializer.data["country"],
                    "unique_id": serializer.data["unique_id"]
                }
                
                return custom_200("Updated Successfully",response_data)
            return custom_404(serializer.errors)
            
        except PatientProfile.DoesNotExist:
            return custom_404("Patient profile not found. Please complete your profile registration.")
        except Exception as e:
            return custom_404(f"Error updating patient profile: {str(e)}")


#get the user by login user
class GetUserByLoginUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        serializer = UserSerializer(user)
        return custom_200(serializer.data)


# book appointment api by patient and also by front office staff that is admin staff and sending notifications
class BookAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def check_doctor_availability(self, doctor_id, date, time):
        try:
            return not Appointment.objects.filter(
                doctor=doctor_id,
                date=date,
                time=time,
                status='Scheduled'
            ).exists()
        except Exception as e:
            print(f"Error checking doctor availability: {str(e)}")
            return False

    def post(self, request):
        doctor_id = request.data.get('doctor')
        appointment_date = request.data.get('date')
        appointment_time = request.data.get('time')

        try:
            # Check if doctor is available
            if not self.check_doctor_availability(doctor_id, appointment_date, appointment_time):
                return custom_404("Doctor is not available at the selected date and time. Please choose another slot.")

            # Get patient user (ProfileUser)
            if 'patient_id' in request.data:
                patient_profile = PatientProfile.objects.get(id=request.data.get('patient_id'))
            else:
                patient_profile = PatientProfile.objects.get(user=request.user)

            patient_user = patient_profile.user  # 👈 Get the ProfileUser from PatientProfile

            # Prepare data for serializer
            appointment_data = request.data.copy()
            appointment_data['patient'] = patient_user.id  # ✅ Correct: pass ProfileUser ID
            appointment_data['status'] = 'Scheduled'

            serializer = BookAppointmentSerializer(data=appointment_data)
            if serializer.is_valid():
                appointment = serializer.save()

                # Update doctor's availability
                doctor_user = appointment.doctor
                doctor_profile = DoctorProfile.objects.get(user=doctor_user)
                doctor_profile.is_available = False
                doctor_profile.save()

                # Notifications
                Notification.objects.create(
                    user=patient_user,
                    appointment=appointment,
                    notification_type='appointment_created',
                    title='Appointment Booked',
                    message=f"Your appointment with Dr. {doctor_user.get_full_name()} on {appointment.date} at {appointment.time} is confirmed."
                )

                Notification.objects.create(
                    user=doctor_user,
                    appointment=appointment,
                    notification_type='appointment_created',
                    title='New Appointment',
                    message=f"You have a new appointment with {patient_user.get_full_name()} on {appointment.date} at {appointment.time}."
                )

                # Emails
                send_email_notification(
                    subject="Your Appointment is Confirmed",
                    message=f"Dear {patient_user.get_full_name()},\n\nYour appointment with Dr. {doctor_user.get_full_name()} is scheduled on {appointment.date} at {appointment.time}.",
                    recipient_list=[patient_user.email]
                )

                send_email_notification(
                    subject="New Appointment Scheduled",
                    message=f"Dear Dr. {doctor_user.get_full_name()},\n\nYou have a new appointment with {patient_user.get_full_name()} on {appointment.date} at {appointment.time}.",
                    recipient_list=[doctor_user.email]
                )

                return custom_200("Appointment booked successfully")

            return custom_404(serializer.errors)

        except PatientProfile.DoesNotExist:
            return custom_404("Patient not found")
        except DoctorProfile.DoesNotExist:
            return custom_404("Doctor profile not found")
        except Exception as e:
            return custom_404(f"Error booking appointment: {str(e)}")


# list all doctors api
class ListAllCardiologist(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            # Get all doctors
            doctors = DoctorProfile.objects.all()
            
            # Serialize the data
            serializer = ListallDcotorsSerializer(doctors, many=True)
            
            # Format the response data
            response_data = []
            for doctor in serializer.data:
                formatted_doctor = {
                    "id": doctor["id"],
                    "user_id":doctor["user"]["id"],
                    "email": doctor["user"]["email"],
                    "first_name": doctor["user"]["first_name"],
                    "last_name": doctor["user"]["last_name"],
                    "role": doctor["user"]["role"],
                    "is_verified": doctor["user"]["is_verified"],
                    "specialization": doctor["specialization"],
                    "experience": doctor["experience"],
                    "availability": doctor["availability"],
                    "fees": doctor["fees"],
                    "is_available": doctor["is_available"],
                    "date_of_birth": doctor["date_of_birth"],
                    "gender": doctor["gender"],
                    "address": doctor["address"],
                    "emergency_contact": doctor["emergency_contact"]
                }
                response_data.append(formatted_doctor)

            return custom_200("Doctors retrieved successfully", response_data)
            
        except Exception as e:
            return custom_404(f"Error fetching doctors: {str(e)}")