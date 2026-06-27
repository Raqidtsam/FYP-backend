from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegionViewSet, DistrictViewSet, EconomicActivityViewSet,
    DistrictActivityViewSet, InvestmentSectorViewSet,
    RecommendationViewSet, UserViewSet
)
from .auth_views import register, login, profile

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'economic-activities', EconomicActivityViewSet)
router.register(r'district-activities', DistrictActivityViewSet)
router.register(r'investment-sectors', InvestmentSectorViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/profile/', profile, name='profile'),
]