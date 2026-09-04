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
    is_investment_officer = models.BooleanField(default=False)
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


class InvestmentLocation(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='investment_locations')
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    land_use = models.CharField(max_length=100, null=True, blank=True)  # Tourism, Residential, Commercial
    distance_to_ocean_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nearby_locations = models.TextField(null=True, blank=True)  # JSON string
    owner_name = models.CharField(max_length=200, null=True, blank=True)
    owner_phone = models.CharField(max_length=50, null=True, blank=True)
    owner_email = models.EmailField(null=True, blank=True)
    owner_address = models.TextField(null=True, blank=True)
    zipa_phone = models.CharField(max_length=50, default='+255 24 223 3026')
    zipa_email = models.EmailField(default='info@zipa.go.tz')
    zipa_address = models.TextField(default='Mazizini, Zanzibar')
    price_per_hectare = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_negotiable = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    investment_type = models.CharField(
        max_length=50,
        choices=[
            ('Tourism', 'Tourism & Hospitality'),
            ('Residential', 'Residential'),
            ('Commercial', 'Commercial'),
            ('Fishing', 'Fishing'),
            ('Agriculture', 'Agriculture'),
            ('Industrial', 'Industrial'),
        ],
        default='Tourism'
    )

    class Meta:
        db_table = 'investment_locations'

    def __str__(self):
        return f"{self.name} - {self.district.name}"


class InAppNotification(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)

    class Meta:
        db_table = 'in_app_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Transaction(models.Model):
    transaction_type = models.CharField(max_length=50)  # Investment, Registration, Search, etc.
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    investment_location = models.ForeignKey(InvestmentLocation, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.created_at}"


