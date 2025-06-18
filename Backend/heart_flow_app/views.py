from django.shortcuts import render
from rest_framework.views import APIView 
from .mixins import *
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from . utils import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
import pyotp

# Create your views here.


# pateint registration api
class PatientRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send OTP
            secret = generate_otp_secret(user.email)
            user.otp_secret = secret
            user.save()
            cache.set(f"otp_secret_{user.email}", secret, timeout=600)
            
            totp = pyotp.TOTP(secret)
            otp = totp.now()
            
            send_mail(
                subject="Your OTP for Registration",
                message=f"Your OTP is {otp}. It will expire in 10 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            
            return custom_200("Patient registered successfully. Please verify your email with OTP.")
        return custom_404(serializer.errors)


# cardiologist-doctors registration api
class CardiologistRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CardiologistRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send OTP
            secret = generate_otp_secret(user.email)
            user.otp_secret = secret
            user.save()
            cache.set(f"otp_secret_{user.email}", secret, timeout=600)
            
            totp = pyotp.TOTP(secret)
            otp = totp.now()
            
            send_mail(
                subject="Your OTP for Registration",
                message=f"Your OTP is {otp}. It will expire in 10 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            
            return custom_200("Cardiologist registered successfully. Please verify your email with OTP.")
        return custom_404(serializer.errors)    

# login api based on roles
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is None:
                return custom_404('Invalid credentials')

            send_otp_via_email(user.email)
            return custom_200('OTP sent to your email')

        return custom_404(serializer.errors)
    

# verify the otp and pass tokens 
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            # 🔐 Fetch OTP secret from cache or fallback to user model
            secret = cache.get(f"otp_secret_{email}")

            if not secret:
                try:
                    user = ProfileUser.objects.get(email=email)
                    secret = user.otp_secret
                except ProfileUser.DoesNotExist:
                    return Response({'error': 'User not found'}, status=404)

                if not secret:
                    return Response({'error': 'OTP expired or not found'}, status=400)

            # ✅ Verify OTP with time window allowance
            totp = pyotp.TOTP(secret)
            if not totp.verify(otp, valid_window=1):
                return Response({'error': 'Invalid OTP'}, status=400)

            try:
                user = ProfileUser.objects.get(email=email)
            except ProfileUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            # ✅ Mark user as verified
            user.is_verified = True
            user.save()

            # 🎟 Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            refresh["user_id"] = user.id
            refresh["role"] = user.role

            # 🔒 Clear OTP from cache
            cache.delete(f"otp_secret_{email}")

            return custom_200("Verification successful", {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': user.id,
                'role': user.role,
                'email': user.email,
                'is_verified': user.is_verified
            })

        return custom_404(serializer.errors)


# resent otp api
class ResendOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return custom_404("Email is required")

        success = send_otp_via_email(email)
        if not success:
            return custom_404("User with this email does not exist")

        return custom_200("OTP sent successfully to email")       