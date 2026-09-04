from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.db import models
from django.db.models import Count, Avg
from .models import (
    User, District, EconomicActivity, DistrictActivity,
    InvestmentLocation, InvestmentSector, Recommendation
)


def is_officer_or_admin(request):
    """Check if user is officer or admin"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, Response({'error': 'Authentication required'}, status=401)

    token = auth_header.replace('Bearer ', '')
    try:
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')
        user = User.objects.get(pk=user_id)

        if not user.is_admin and not user.is_investment_officer:
            return None, Response({'error': 'Officer access required'}, status=403)

        return user, None
    except Exception as e:
        return None, Response({'error': str(e)}, status=401)


def validate_coordinates(latitude, longitude):
    """Validate latitude and longitude values"""
    try:
        lat = float(latitude)
        lng = float(longitude)
    except (ValueError, TypeError):
        return False, 'Latitude and longitude must be valid numbers'

    if lat < -90 or lat > 90:
        return False, 'Latitude must be between -90 and 90'

    if lng < -180 or lng > 180:
        return False, 'Longitude must be between -180 and 180'

    # Zanzibar bounds validation
    if lat < -6.5 or lat > -4.8:
        return False, 'Latitude must be within Zanzibar bounds (-6.5 to -4.8)'

    if lng < 39.1 or lng > 39.9:
        return False, 'Longitude must be within Zanzibar bounds (39.1 to 39.9)'

    return True, None


# ============ DASHBOARD ============

@api_view(['GET'])
def officer_dashboard(request):
    """Officer dashboard stats"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    return Response({
        'officer': user.full_name,
        'total_investment_areas': InvestmentLocation.objects.count(),
        'total_districts': District.objects.count(),
        'total_activities': EconomicActivity.objects.count(),
        'total_recommendations': Recommendation.objects.count(),
        'pending_locations': InvestmentLocation.objects.filter(description__isnull=True).count(),
    })


# ============ INVESTMENT LOCATIONS ============

@api_view(['GET'])
def officer_locations(request):
    """Get all investment locations for management"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    locations = InvestmentLocation.objects.all().values(
        'id', 'name', 'latitude', 'longitude', 'district__name',
        'investment_type', 'land_use', 'price_per_hectare',
        'distance_to_ocean_km', 'description', 'district_id'
    )
    return Response(list(locations))


@api_view(['POST'])
def officer_add_location(request):
    """Add new investment location"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    name = request.data.get('name')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not name or not latitude or not longitude:
        return Response({'error': 'name, latitude, and longitude are required'}, status=400)

    # Validate coordinates
    is_valid, error_msg = validate_coordinates(latitude, longitude)
    if not is_valid:
        return Response({'error': error_msg}, status=400)

    try:
        district = District.objects.first()
        if not district:
            return Response({'error': 'No districts available'}, status=400)

        loc = InvestmentLocation.objects.create(
            district=district,
            name=name,
            latitude=float(latitude),
            longitude=float(longitude),
            size_hectares=request.data.get('size_hectares', 10.0),
            land_use=request.data.get('land_use', 'Investment'),
            investment_type=request.data.get('investment_type', 'Tourism'),
            distance_to_ocean_km=request.data.get('distance_to_ocean_km', 0.5),
            price_per_hectare=request.data.get('price_per_hectare', 100000),
            description=request.data.get('description', 'Added by officer'),
            nearby_locations='[{"name": "Stone Town", "distance_km": 15}]',
            owner_name='',
            owner_phone='',
            owner_email='',
            owner_address='',
        )
        return Response({'message': 'Location added', 'id': loc.pk})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['PUT'])
def officer_update_location(request, location_id):
    """Update investment location"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    try:
        loc = InvestmentLocation.objects.get(pk=location_id)

        # Validate coordinates if provided
        if 'latitude' in request.data or 'longitude' in request.data:
            new_lat = request.data.get('latitude', loc.latitude)
            new_lng = request.data.get('longitude', loc.longitude)
            is_valid, error_msg = validate_coordinates(new_lat, new_lng)
            if not is_valid:
                return Response({'error': error_msg}, status=400)

        if 'name' in request.data:
            loc.name = request.data['name']
        if 'land_use' in request.data:
            loc.land_use = request.data['land_use']
        if 'investment_type' in request.data:
            loc.investment_type = request.data['investment_type']
        if 'price_per_hectare' in request.data:
            try:
                loc.price_per_hectare = float(request.data['price_per_hectare'])
            except (ValueError, TypeError):
                return Response({'error': 'Price must be a valid number'}, status=400)
        if 'description' in request.data:
            loc.description = request.data['description']
        if 'distance_to_ocean_km' in request.data:
            try:
                loc.distance_to_ocean_km = float(request.data['distance_to_ocean_km'])
            except (ValueError, TypeError):
                return Response({'error': 'Distance must be a valid number'}, status=400)
        if 'latitude' in request.data:
            loc.latitude = float(request.data['latitude'])
        if 'longitude' in request.data:
            loc.longitude = float(request.data['longitude'])

        loc.save()
        return Response({'message': 'Location updated'})
    except InvestmentLocation.DoesNotExist:
        return Response({'error': 'Location not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['DELETE'])
def officer_delete_location(request, location_id):
    """Delete investment location"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    try:
        loc = InvestmentLocation.objects.get(pk=location_id)
        loc.delete()
        return Response({'message': 'Location deleted'})
    except InvestmentLocation.DoesNotExist:
        return Response({'error': 'Location not found'}, status=404)


# ============ ECONOMIC ACTIVITIES ============

@api_view(['GET'])
def officer_activities(request):
    """Get all economic activities"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    activities = EconomicActivity.objects.all().values('id', 'name', 'category', 'description')
    return Response(list(activities))


@api_view(['POST'])
def officer_add_activity(request):
    """Add economic activity"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    name = request.data.get('name')
    if not name:
        return Response({'error': 'Activity name required'}, status=400)

    try:
        activity = EconomicActivity.objects.create(
            name=name,
            category=request.data.get('category', 'General'),
            description=request.data.get('description', ''),
        )
        return Response({'message': 'Activity added', 'id': activity.pk})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['PUT'])
def officer_update_activity(request, activity_id):
    """Update economic activity"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    try:
        activity = EconomicActivity.objects.get(pk=activity_id)
        if 'name' in request.data:
            activity.name = request.data['name']
        if 'category' in request.data:
            activity.category = request.data['category']
        if 'description' in request.data:
            activity.description = request.data['description']
        activity.save()
        return Response({'message': 'Activity updated'})
    except EconomicActivity.DoesNotExist:
        return Response({'error': 'Activity not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['DELETE'])
def officer_delete_activity(request, activity_id):
    """Delete economic activity"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    try:
        activity = EconomicActivity.objects.get(pk=activity_id)
        activity.delete()
        return Response({'message': 'Activity deleted'})
    except EconomicActivity.DoesNotExist:
        return Response({'error': 'Activity not found'}, status=404)


# ============ REPORTS ============

@api_view(['GET'])
def officer_reports(request):
    """Get investment reports for monitoring"""
    user, error = is_officer_or_admin(request)
    if error:
        return error

    by_type = list(
        InvestmentLocation.objects.values('investment_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    by_district = list(
        InvestmentLocation.objects.values('district__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    avg_price = InvestmentLocation.objects.aggregate(avg=Avg('price_per_hectare'))['avg']

    return Response({
        'by_type': by_type,
        'by_district': by_district,
        'total_locations': InvestmentLocation.objects.count(),
        'avg_price': avg_price or 0,
    })