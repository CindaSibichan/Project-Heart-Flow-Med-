from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from . manager import CustomUserManager


class ProfileUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Cardiologist', 'Cardiologist'),
        ('Nurse', 'Nurse'),
        ('Sonographer', 'Sonographer'),
        ('Admin Staff', 'Admin Staff'),
        ('Patient', 'Patient'),
        ('Group Manager', 'Group Manager'),
        ('IT Staff', 'IT Staff'),
        ('General Practitioner', 'General Practitioner'),
    ]
    username = None  # Remove the username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp_secret = models.CharField(max_length=32, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'  # Important
    REQUIRED_FIELDS = []  # Since email is the only required field

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class PatientProfile(models.Model):
    user = models.OneToOneField(ProfileUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Patient'})
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_id = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.user.first_name}-{self.user.last_name}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(ProfileUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Cardiologist'})
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100,null=True,blank=True)
    experience = models.IntegerField(null=True,blank=True)
    availability = models.CharField(max_length=100,null=True,blank=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    is_available = models.BooleanField(default=True)

    

    def __str__(self):
        return f"{self.user.first_name}-{self.user.last_name}"
    
class Appointment(models.Model):
    patient = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name='patients', limit_choices_to={'role': 'Patient'})
    doctor = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name='doctors',limit_choices_to={'role': 'Cardiologist'})
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])
    notes = models.TextField(blank=True)
    

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date}"



class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_reminder', 'Appointment Reminder'),
    )

    user = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.user.first_name}"
