from rest_framework import serializers
from . models import *
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from . utils import *

# class RegistrationSerailizer
class PatientRegistrationSerializer(serializers.ModelSerializer):
    # Include patient-specific fields
    date_of_birth = serializers.DateField()
    gender = serializers.CharField(max_length=10)
    address = serializers.CharField()
    emergency_contact = serializers.CharField(max_length=100)
    insurance_provider = serializers.CharField(max_length=100, required=False, allow_blank=True)
    insurance_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    country = serializers.CharField(max_length=55 , required=False , allow_blank=True)

    class Meta:
        model = ProfileUser
        fields = ['email', 'password', 'phone', 'date_of_birth', 'gender', 'address','first_name','last_name',
                  'emergency_contact', 'insurance_provider', 'insurance_id', 'country']

    def create(self, validated_data):
        # Extract PatientProfile fields
        patient_data = {
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'address': validated_data.pop('address'),
            'emergency_contact': validated_data.pop('emergency_contact'),
            'insurance_provider': validated_data.pop('insurance_provider', ''),
            'insurance_id': validated_data.pop('insurance_id', ''),
            'country': validated_data.pop('country',''),
        }

        # Create user with role 'Patient'
        user = ProfileUser.objects.create(
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            role='Patient',
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=make_password(validated_data['password']),
            is_verified=False
        )
        patient_id = generate_patient_id()
        # Create patient profile
        PatientProfile.objects.create(user=user, unique_id = patient_id,**patient_data)

        return user

# login
class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# verify otp 
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

# doctor registration serializer
class CardiologistRegistrationSerializer(serializers.ModelSerializer):
    emergency_contact = serializers.CharField(max_length=100)
    address = serializers.CharField()
    gender = serializers.CharField(max_length=10)
    date_of_birth = serializers.DateField()
    specialization = serializers.CharField(max_length=100,required=False,allow_blank=True)
    experience = serializers.IntegerField(required=False,allow_null=True)
    availability = serializers.CharField(max_length=100,required=False,allow_blank=True)
    fees = serializers.DecimalField(max_digits=10, decimal_places=2,required=False,allow_null=True)

    class Meta:
        model = ProfileUser
        fields = ['email', 'password', 'phone', 'date_of_birth', 'gender', 'address','first_name','last_name',
                  'emergency_contact', 'specialization', 'experience', 'availability', 'fees']

    def create(self, validated_data):
        user = ProfileUser.objects.create(
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            phone=validated_data.get('phone', ''),
            role='Cardiologist',
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_verified=False
        )
        doctor_data = {
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'address': validated_data.pop('address'),
            'emergency_contact': validated_data.pop('emergency_contact'),
            'specialization': validated_data.pop('specialization',''),
            'experience': validated_data.pop('experience',0),
            'availability': validated_data.pop('availability',''),
            'fees': validated_data.pop('fees',0.0),
        }
        DoctorProfile.objects.create(user=user, **doctor_data)
        return user


