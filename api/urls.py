from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegionViewSet, DistrictViewSet, EconomicActivityViewSet,
    DistrictActivityViewSet, InvestmentSectorViewSet,
    RecommendationViewSet, UserViewSet
)

from .auth_views import (
    register, login, profile, update_profile,
    forgot_password, verify_otp, reset_password
)

from .admin_views import (
    admin_dashboard, admin_users, toggle_user_status,
    toggle_admin_status, delete_user, admin_districts,
    update_district, admin_activities, admin_recommendations
)

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
    path('auth/profile/update/', update_profile, name='update_profile'),

    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/toggle-admin/', toggle_admin_status, name='toggle_admin_status'),
    path('admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('admin/districts/', admin_districts, name='admin_districts'),
    path('admin/districts/<int:district_id>/update/', update_district, name='update_district'),
    path('admin/activities/', admin_activities, name='admin_activities'),
    path('admin/recommendations/', admin_recommendations, name='admin_recommendations'),

    path('auth/forgot-password/', forgot_password, name='forgot_password'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    path('auth/reset-password/', reset_password, name='reset_password'),

]