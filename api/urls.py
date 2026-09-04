from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegionViewSet, DistrictViewSet, EconomicActivityViewSet,
    DistrictActivityViewSet, InvestmentSectorViewSet,
    RecommendationViewSet, UserViewSet, MessageViewSet,
    InvestmentLocationViewSet, gis_search
)

from .auth_views import (
    register, login, profile, update_profile,
    forgot_password, verify_otp, reset_password,
    verify_register_otp, verify_login_otp
)

from .admin_views import (
    admin_dashboard, admin_users, toggle_user_status,
    toggle_admin_status, delete_user, admin_districts,
    update_district, admin_activities, admin_recommendations,
    admin_system_info, admin_backup_database,
    admin_test_email, admin_audit_log, admin_generate_recommendations,
    admin_add_recommendation, admin_update_recommendation,
    admin_delete_recommendation, admin_recommendation_stats, admin_sectors,
    register_fcm_token, admin_send_notification,
    admin_user_detail, admin_reset_password, admin_reports, admin_export_report, admin_send_in_app_notification,
    get_in_app_notifications, mark_notification_read
)

from .officer_views import (
    officer_dashboard, officer_locations, officer_add_location,
    officer_update_location, officer_delete_location,
    officer_activities, officer_add_activity, officer_update_activity,
    officer_reports, officer_delete_activity
)

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'economic-activities', EconomicActivityViewSet)
router.register(r'district-activities', DistrictActivityViewSet)
router.register(r'investment-sectors', InvestmentSectorViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'users', UserViewSet)
router.register(r'investment-locations', InvestmentLocationViewSet, basename='investment-locations')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', register, name='register'),
    path('auth/verify-register-otp/', verify_register_otp, name='verify_register_otp'),
    path('auth/login/', login, name='login'),
    path('auth/verify-login-otp/', verify_login_otp, name='verify_login_otp'),
    path('auth/profile/', profile, name='profile'),
    path('auth/profile/update/', update_profile, name='update_profile'),
    path('auth/forgot-password/', forgot_password, name='forgot_password'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    path('auth/reset-password/', reset_password, name='reset_password'),
    path('auth/register-fcm-token/', register_fcm_token, name='register_fcm_token'),

    # GIS
    path('gis/search/', gis_search, name='gis_search'),

    # Admin - Dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),

    # Admin - Users
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/detail/', admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/toggle-admin/', toggle_admin_status, name='toggle_admin_status'),
    path('admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('admin/users/<int:user_id>/reset-password/', admin_reset_password, name='admin_reset_password'),

    # Admin - Districts
    path('admin/districts/', admin_districts, name='admin_districts'),
    path('admin/districts/<int:district_id>/update/', update_district, name='update_district'),

    # Admin - Activities
    path('admin/activities/', admin_activities, name='admin_activities'),

    # Admin - Recommendations
    path('admin/recommendations/', admin_recommendations, name='admin_recommendations'),
    path('admin/recommendations/generate/', admin_generate_recommendations, name='admin_generate_recommendations'),
    path('admin/recommendations/add/', admin_add_recommendation, name='admin_add_recommendation'),
    path('admin/recommendations/<int:rec_id>/update/', admin_update_recommendation, name='admin_update_recommendation'),
    path('admin/recommendations/<int:rec_id>/delete/', admin_delete_recommendation, name='admin_delete_recommendation'),
    path('admin/recommendations/stats/', admin_recommendation_stats, name='admin_recommendation_stats'),
    path('admin/sectors/', admin_sectors, name='admin_sectors'),
    path('admin/notifications/in-app/send/', admin_send_in_app_notification, name='admin_send_in_app_notification'),
    path('notifications/', get_in_app_notifications, name='get_in_app_notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),

    # Admin - System
    path('admin/system/info/', admin_system_info, name='admin_system_info'),
    path('admin/system/backup/', admin_backup_database, name='admin_backup_database'),
    path('admin/system/test-email/', admin_test_email, name='admin_test_email'),
    path('admin/system/audit-log/', admin_audit_log, name='admin_audit_log'),
    path('admin/reports/', admin_reports, name='admin_reports'),
    path('admin/reports/export/', admin_export_report, name='admin_export_report'),

    # Admin - Notifications
    path('admin/notifications/send/', admin_send_notification, name='admin_send_notification'),

    path('officer/dashboard/', officer_dashboard, name='officer_dashboard'),
    path('officer/locations/', officer_locations, name='officer_locations'),
    path('officer/locations/add/', officer_add_location, name='officer_add_location'),
    path('officer/locations/<int:location_id>/update/', officer_update_location, name='officer_update_location'),
    path('officer/locations/<int:location_id>/delete/', officer_delete_location, name='officer_delete_location'),
    path('officer/activities/', officer_activities, name='officer_activities'),
    path('officer/activities/add/', officer_add_activity, name='officer_add_activity'),
    path('officer/activities/<int:activity_id>/update/', officer_update_activity, name='officer_update_activity'),
    path('officer/reports/', officer_reports, name='officer_reports'),
    path('officer/activities/<int:activity_id>/delete/', officer_delete_activity, name='officer_delete_activity'),

    # Router (must be last)
    path('', include(router.urls)),
]