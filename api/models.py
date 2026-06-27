from django.db import models
from django.contrib.auth.hashers import make_password


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
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk or not self.password_hash.startswith('pbkdf2_sha256$'):
            self.password_hash = make_password(self.password_hash)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'users'