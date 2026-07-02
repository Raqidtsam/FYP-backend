from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User, District, Region, EconomicActivity, InvestmentSector, Recommendation


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