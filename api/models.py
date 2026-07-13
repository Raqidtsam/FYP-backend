from django.db import models
from django.contrib.auth.hashers import make_password
import random
from datetime import timedelta
from django.utils import timezone


class Region(models.Model):
    name = models.CharField(max_length=100)
    island = models.CharField(max_length=50)  # 'Unguja' or 'Pemba'
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    boundary = models.JSONField(null=True, blank=True)  # Store polygon coordinates

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'regions'


class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    boundary = models.JSONField(null=True, blank=True)  # Store polygon coordinates

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    class Meta:
        db_table = 'districts'


class EconomicActivity(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)  # Kilimo, Uvuvi, Biashara, Utalii
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'economic_activities'


class DistrictActivity(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='district_activities')
    activity = models.ForeignKey(EconomicActivity, on_delete=models.CASCADE)
    dominance = models.CharField(max_length=50)  # 'High', 'Medium', 'Low'

    def __str__(self):
        return f"{self.activity.name} - {self.district.name} ({self.dominance})"

    class Meta:
        db_table = 'district_activities'


class InvestmentSector(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    estimated_roi = models.CharField(max_length=100, null=True, blank=True)
    capital_required = models.CharField(max_length=100)  # 'Low', 'Medium', 'High'

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'investment_sectors'


class Recommendation(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='recommendations')
    sector = models.ForeignKey(InvestmentSector, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.sector.name} in {self.district.name} - Score: {self.score}"

    class Meta:
        db_table = 'recommendations'


class User(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Only hash password for new users or if password changed
        if self._state.adding:  # New object
            if not self.password_hash.startswith('pbkdf2_sha256$'):
                self.password_hash = make_password(self.password_hash)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'users'


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_otp(cls, user):
        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Expire in 10 minutes
        expires_at = timezone.now() + timedelta(minutes=10)

        # Create token
        token = cls.objects.create(
            user=user,
            otp_code=otp,
            expires_at=expires_at
        )

        return token

    class Meta:
        db_table = 'password_reset_tokens'

class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.CharField(max_length=255, unique=True)
    device = models.CharField(max_length=50, default='android')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fcm_tokens'

    def __str__(self):

        return f"{self.user.email} - {self.device}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.full_name}: {self.subject}"