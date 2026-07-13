from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegionViewSet, DistrictViewSet, EconomicActivityViewSet,
    DistrictActivityViewSet, InvestmentSectorViewSet,
    RecommendationViewSet, UserViewSet, MessageViewSet
)

from .auth_views import (
    register, login, profile, update_profile,
    forgot_password, verify_otp, reset_password,
    verify_register_otp, verify_login_otp
)

from .admin_views import (
    admin_dashboard, admin_users, toggle_user_status,
    toggle_admin_status, delete_user, admin_districts,
    update_district, admin_activities, admin_recommendations, admin_system_info, admin_backup_database,
    admin_test_email, admin_audit_log, admin_generate_recommendations, admin_add_recommendation,
    admin_update_recommendation, admin_delete_recommendation, admin_recommendation_stats, admin_sectors,
    register_fcm_token, admin_send_notification

)

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'economic-activities', EconomicActivityViewSet)
router.register(r'district-activities', DistrictActivityViewSet)
router.register(r'investment-sectors', InvestmentSectorViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'messages', MessageViewSet)
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
    path('auth/verify-register-otp/', verify_register_otp, name='verify_register_otp'),
    path('auth/verify-login-otp/', verify_login_otp, name='verify_login_otp'),

    path('admin/system/info/', admin_system_info, name='admin_system_info'),
    path('admin/system/backup/', admin_backup_database, name='admin_backup_database'),
    path('admin/system/test-email/', admin_test_email, name='admin_test_email'),
    path('admin/system/audit-log/', admin_audit_log, name='admin_audit_log'),

    path('admin/recommendations/generate/', admin_generate_recommendations, name='admin_generate_recommendations'),
    path('admin/recommendations/add/', admin_add_recommendation, name='admin_add_recommendation'),
    path('admin/recommendations/<int:rec_id>/update/', admin_update_recommendation, name='admin_update_recommendation'),
    path('admin/recommendations/<int:rec_id>/delete/', admin_delete_recommendation, name='admin_delete_recommendation'),
    path('admin/recommendations/stats/', admin_recommendation_stats, name='admin_recommendation_stats'),
    path('admin/sectors/', admin_sectors, name='admin_sectors'),

    path('auth/register-fcm-token/', register_fcm_token, name='register_fcm_token'),
    path('admin/notifications/send/', admin_send_notification, name='admin_send_notification'),

]