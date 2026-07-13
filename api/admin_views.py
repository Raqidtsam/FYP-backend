from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User, District, Region, EconomicActivity, InvestmentSector, Recommendation
from django.db import models
import os
from django.utils import timezone
from django.core.management import call_command
from django.core.mail import send_mail
from .recommendation_engine import engine
from django.conf import settings as django_settings


@api_view(['GET'])
def admin_dashboard(request):
    """Get dashboard stats"""
    total_users = User.objects.count()
    total_districts = District.objects.count()
    total_regions = Region.objects.count()
    total_sectors = InvestmentSector.objects.count()
    total_recommendations = Recommendation.objects.count()

    recent_users = User.objects.order_by('-created_at')[:5].values(
        'id', 'full_name', 'email', 'nationality', 'created_at'
    )

    return Response({
        'stats': {
            'total_users': total_users,
            'total_districts': total_districts,
            'total_regions': total_regions,
            'total_sectors': total_sectors,
            'total_recommendations': total_recommendations,
        },
        'recent_users': list(recent_users),
    })


@api_view(['GET'])
def admin_users(request):
    """Get all users"""
    users = User.objects.all().values(
        'id', 'full_name', 'email', 'nationality', 'contact', 'is_active', 'is_admin', 'created_at'
    )
    return Response(list(users))


@api_view(['PUT'])
def toggle_user_status(request, user_id):
    """Activate/Deactivate user"""
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        return Response(
            {'message': f'User {"activated" if user.is_active else "deactivated"}', 'is_active': user.is_active})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['PUT'])
def toggle_admin_status(request, user_id):
    """Make/Remove admin"""
    try:
        user = User.objects.get(pk=user_id)
        user.is_admin = not user.is_admin
        user.save()
        return Response({'message': f'Admin status: {user.is_admin}', 'is_admin': user.is_admin})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['DELETE'])
def delete_user(request, user_id):
    """Delete user"""
    try:
        user = User.objects.get(pk=user_id)
        # Prevent deleting yourself
        if request.admin_user and request.admin_user.pk == user.pk:
            return Response({'error': 'Cannot delete yourself'}, status=400)
        user.delete()
        return Response({'message': 'User deleted'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
def admin_districts(request):
    """Get all districts with region info"""
    districts = District.objects.select_related('region').all().values(
        'id', 'name', 'latitude', 'longitude', 'region__name', 'region__island'
    )
    return Response(list(districts))


@api_view(['PUT'])
def update_district(request, district_id):
    """Update district"""
    try:
        district = District.objects.get(pk=district_id)
        if 'name' in request.data:
            district.name = request.data['name']
        if 'latitude' in request.data:
            district.latitude = request.data['latitude']
        if 'longitude' in request.data:
            district.longitude = request.data['longitude']
        district.save()
        return Response({'message': 'District updated'})
    except District.DoesNotExist:
        return Response({'error': 'District not found'}, status=404)


@api_view(['GET'])
def admin_activities(request):
    """Get all economic activities"""
    activities = EconomicActivity.objects.all().values('id', 'name', 'category', 'description')
    return Response(list(activities))


@api_view(['GET'])
def admin_recommendations(request):
    """Get all recommendations"""
    recommendations = Recommendation.objects.select_related('district', 'sector').all().values(
        'id', 'district__name', 'sector__name', 'score', 'reason'
    ).order_by('-score')
    return Response(list(recommendations))


@api_view(['POST'])
def admin_generate_recommendations(request):
    """Generate AI recommendations for all districts or specific one"""
    district_id = request.data.get('district_id')
    try:
        count = engine.generate_recommendations(district_id)
        return Response({
            'message': f'Successfully generated {count} recommendations',
            'count': count
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def admin_add_recommendation(request):
    """Manually add a recommendation"""
    district_id = request.data.get('district_id')
    sector_id = request.data.get('sector_id')
    score = request.data.get('score', 50)
    reason = request.data.get('reason', '')

    if not district_id or not sector_id:
        return Response({'error': 'district_id and sector_id required'}, status=400)

    try:
        district = District.objects.get(pk=district_id)
        sector = InvestmentSector.objects.get(pk=sector_id)
    except (District.DoesNotExist, InvestmentSector.DoesNotExist):
        return Response({'error': 'Invalid district or sector'}, status=404)

    rec = Recommendation.objects.create(
        district=district,
        sector=sector,
        score=score,
        reason=reason
    )
    return Response({
        'message': 'Recommendation added',
        'id': rec.pk,
        'district': district.name,
        'sector': sector.name,
        'score': rec.score
    })


@api_view(['PUT'])
def admin_update_recommendation(request, rec_id):
    """Update recommendation score or reason"""
    score = request.data.get('score')
    reason = request.data.get('reason')

    try:
        rec = Recommendation.objects.get(pk=rec_id)
        if score is not None:
            rec.score = score
        if reason is not None:
            rec.reason = reason
        rec.save()
        return Response({'message': 'Recommendation updated'})
    except Recommendation.DoesNotExist:
        return Response({'error': 'Recommendation not found'}, status=404)


@api_view(['DELETE'])
def admin_delete_recommendation(request, rec_id):
    """Delete a recommendation"""
    try:
        rec = Recommendation.objects.get(pk=rec_id)
        rec.delete()
        return Response({'message': 'Recommendation deleted'})
    except Recommendation.DoesNotExist:
        return Response({'error': 'Recommendation not found'}, status=404)


@api_view(['GET'])
def admin_recommendation_stats(request):
    """Get recommendation statistics"""
    total = Recommendation.objects.count()
    by_district = Recommendation.objects.values('district__name').annotate(
        count=models.Count('id'),
        avg_score=models.Avg('score')
    ).order_by('-count')[:10]

    by_sector = Recommendation.objects.values('sector__name').annotate(
        count=models.Count('id'),
        avg_score=models.Avg('score')
    ).order_by('-count')[:10]

    return Response({
        'total': total,
        'by_district': list(by_district),
        'by_sector': list(by_sector),
    })


@api_view(['GET'])
def admin_sectors(request):
    """Get all investment sectors"""
    sectors = InvestmentSector.objects.all().values('id', 'name', 'capital_required', 'estimated_roi', 'description')
    return Response(list(sectors))


# ============ SYSTEM SETTINGS ============

@api_view(['GET'])
def admin_system_info(request):
    """Get system information"""
    total_users = User.objects.count()
    total_districts = District.objects.count()
    total_recommendations = Recommendation.objects.count()
    db_size = 'N/A'

    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_database_size('smart_geo_investment')")
            size_bytes = cursor.fetchone()[0]
            db_size = f'{size_bytes / (1024 * 1024):.1f} MB'
    except:
        pass

    return Response({
        'app_name': 'Smart Geo Investment',
        'version': '1.0.0',
        'total_users': total_users,
        'total_districts': total_districts,
        'total_recommendations': total_recommendations,
        'database_size': db_size,
        'server_time': timezone.now().isoformat(),
        'debug_mode': django_settings.DEBUG,
    })


@api_view(['POST'])
def admin_backup_database(request):
    """Backup database"""
    try:
        backup_dir = os.path.join(django_settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.sql'
        filepath = os.path.join(backup_dir, filename)

        # Run pg_dump
        os.system(f'pg_dump -U smart_geo_user -h localhost smart_geo_investment > {filepath}')

        return Response({
            'message': 'Backup created successfully',
            'filename': filename,
            'path': filepath
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def admin_test_email(request):
    """Test email configuration"""
    test_email = request.data.get('email', 'admin@smartgeo.com')
    try:
        send_mail(
            'Smart Geo Investment - Test Email',
            'This is a test email from Smart Geo Investment admin panel.',
            django_settings.DEFAULT_FROM_EMAIL,
            [test_email],
            fail_silently=False,
        )
        return Response({'message': f'Test email sent to {test_email}'})
    except Exception as e:
        return Response({'error': f'Email failed: {str(e)}'}, status=500)


@api_view(['GET'])
def admin_audit_log(request):
    """Get recent admin activity"""
    # Simple audit - return recent registered users and recommendations
    recent_users = User.objects.order_by('-created_at')[:20].values(
        'id', 'full_name', 'email', 'created_at'
    )
    recent_recs = Recommendation.objects.order_by('-id')[:20].values(
        'id', 'district__name', 'sector__name', 'score', 'id'
    )

    return Response({
        'recent_users': list(recent_users),
        'recent_recommendations': list(recent_recs),
    })


from .models import FCMToken
from .notifications import send_multicast_notification
from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@csrf_exempt
def register_fcm_token(request):
    """Register FCM token for a user"""
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token required'}, status=400)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Authentication required'}, status=401)

    jwt_token = auth_header.replace('Bearer ', '')
    try:
        access_token = AccessToken(jwt_token)
        user_id = access_token.get('user_id')
        user = User.objects.get(pk=user_id)

        # Update or create token
        FCMToken.objects.update_or_create(
            token=token,
            defaults={'user': user, 'device': request.data.get('device', 'android')}
        )
        return Response({'message': 'Token registered'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def admin_send_notification(request):
    """Admin sends push notification"""
    title = request.data.get('title', 'Smart Geo Investment')
    body = request.data.get('body', '')
    user_ids = request.data.get('user_ids', [])  # Empty = all users

    if not body:
        return Response({'error': 'Message body required'}, status=400)

    # Get FCM tokens
    tokens_query = FCMToken.objects.all()
    if user_ids:
        tokens_query = tokens_query.filter(user_id__in=user_ids)

    tokens = list(tokens_query.values_list('token', flat=True))

    if not tokens:
        return Response({'error': 'No device tokens found'}, status=400)

    # Send notification
    data = {
        'type': 'investment_alert',
        'screen': 'dashboard',
    }

    result = send_multicast_notification(tokens, title, body, data)

    return Response({
        'message': 'Notification sent',
        'total_tokens': len(tokens),
        'success': result.get('success_count', 0),
        'failed': result.get('failure_count', 0),
    })