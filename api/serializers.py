from rest_framework import serializers
from .models import (
    Region, District, EconomicActivity, DistrictActivity,
    InvestmentSector, Recommendation, User
)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class EconomicActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicActivity
        fields = '__all__'


class DistrictActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictActivity
        fields = '__all__'


class InvestmentSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentSector
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password_hash': {'write_only': True}}