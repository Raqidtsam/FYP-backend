from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from django.db import models
import json

from .models import (
    Region, District, EconomicActivity, DistrictActivity,
    InvestmentSector, Recommendation, User, InvestmentLocation, Message
)
from .serializers import (
    RegionSerializer, DistrictSerializer, EconomicActivitySerializer,
    DistrictActivitySerializer, InvestmentSectorSerializer,
    RecommendationSerializer, UserSerializer
)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class EconomicActivityViewSet(viewsets.ModelViewSet):
    queryset = EconomicActivity.objects.all()
    serializer_class = EconomicActivitySerializer


class DistrictActivityViewSet(viewsets.ModelViewSet):
    queryset = DistrictActivity.objects.all()
    serializer_class = DistrictActivitySerializer


class InvestmentSectorViewSet(viewsets.ModelViewSet):
    queryset = InvestmentSector.objects.all()
    serializer_class = InvestmentSectorSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

    @action(detail=False, methods=['get'])
    def by_district(self, request):
        district_id = request.query_params.get('district_id')
        if district_id:
            recommendations = Recommendation.objects.filter(
                district_id=district_id
            ).order_by('-score')
            serializer = self.get_serializer(recommendations, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=False, methods=['post'])
    def generate_ai(self, request):
        """Generate AI recommendations"""
        district_id = request.data.get('district_id')

        try:
            from .recommendation_engine import engine
            count = engine.generate_recommendations(district_id)
            return Response({
                'message': f'Generated {count} recommendations successfully',
                'count': count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    @action(detail=False, methods=['get'])
    def by_region(self, request):
        region_id = request.query_params.get('region_id')
        if region_id:
            districts = District.objects.filter(region_id=region_id)
            serializer = self.get_serializer(districts, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get district with activities"""
        try:
            district = District.objects.get(pk=pk)
            activities = DistrictActivity.objects.filter(district=district).select_related('activity')

            return Response({
                'id': district.pk,
                'name': district.name,
                'latitude': district.latitude,
                'longitude': district.longitude,
                'region': district.region.name,
                'island': district.region.island,
                'activities': [
                    {
                        'name': da.activity.name,
                        'category': da.activity.category,
                        'description': da.activity.description,
                        'dominance': da.dominance,
                    }
                    for da in activities
                ],
            })
        except District.DoesNotExist:
            return Response({'error': 'District not found'}, status=404)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()

    def get_queryset(self):
        token = self.request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                user = User.objects.get(pk=user_id)
                if user.is_admin:
                    return Message.objects.filter(parent__isnull=True)
                else:
                    return Message.objects.filter(
                        models.Q(sender_id=user_id) | models.Q(receiver_id=user_id)
                    ).filter(parent__isnull=True).distinct()
            except:
                pass
        return Message.objects.none()

    def create(self, request, *args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response({'error': 'Auth required'}, status=401)
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')

            admin = User.objects.filter(is_admin=True).first()

            msg = Message.objects.create(
                sender_id=user_id,
                receiver=admin,
                subject=request.data.get('subject', 'No Subject'),
                body=request.data.get('body', ''),
            )
            return Response({
                'message': 'Message sent',
                'id': msg.pk,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        """Admin sends broadcast message to all users"""
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response({'error': 'Auth required'}, status=401)

        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            admin = User.objects.get(pk=user_id)

            if not admin.is_admin:
                return Response({'error': 'Admin access required'}, status=403)

            subject = request.data.get('subject', 'Broadcast')
            body = request.data.get('body', '')

            if not body:
                return Response({'error': 'Message body required'}, status=400)

            users = User.objects.filter(is_admin=False, is_active=True)
            count = 0

            for user in users:
                Message.objects.create(
                    sender=admin,
                    receiver=user,
                    subject=subject,
                    body=body,
                )
                count += 1

            return Response({
                'message': f'Broadcast sent to {count} users',
                'count': count,
            })
        except User.DoesNotExist:
            return Response({'error': 'Admin not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Admin replies to a message"""
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response({'error': 'Auth required'}, status=401)
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')

            parent_msg = Message.objects.get(pk=pk)

            reply = Message.objects.create(
                sender_id=user_id,
                receiver=parent_msg.sender,
                subject=f"Re: {parent_msg.subject}",
                body=request.data.get('body', ''),
                parent=parent_msg,
            )
            return Response({'message': 'Reply sent', 'id': reply.pk})
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        try:
            msg = Message.objects.get(pk=pk)
            msg.is_read = True
            msg.save()
            return Response({'message': 'Marked as read'})
        except Message.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                user = User.objects.get(pk=user_id)
                if user.is_admin:
                    count = Message.objects.filter(is_read=False, parent__isnull=True).count()
                else:
                    count = Message.objects.filter(receiver_id=user_id, is_read=False).count()
                return Response({'count': count})
            except:
                pass
        return Response({'count': 0})


class InvestmentLocationViewSet(viewsets.ViewSet):
    """Investment locations - ViewSet (no serializer needed)"""

    def list(self, request):
        district_id = request.query_params.get('district_id')
        investment_type = request.query_params.get('investment_type')

        locations = InvestmentLocation.objects.all()

        if district_id:
            locations = locations.filter(district_id=district_id)

        if investment_type:
            locations = locations.filter(investment_type=investment_type)

        data = []
        for loc in locations:
            data.append({
                'id': loc.pk,
                'name': loc.name,
                'latitude': float(loc.latitude),
                'longitude': float(loc.longitude),
                'district_id': loc.district_id,
                'district_name': loc.district.name,
                'size_hectares': float(loc.size_hectares) if loc.size_hectares else None,
                'land_use': loc.land_use,
                'investment_type': loc.investment_type,
                'distance_to_ocean_km': float(loc.distance_to_ocean_km) if loc.distance_to_ocean_km else None,
                'description': loc.description,
            })
        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            loc = InvestmentLocation.objects.get(pk=pk)
            nearby = []
            if loc.nearby_locations:
                try:
                    nearby = json.loads(loc.nearby_locations)
                except:
                    nearby = []

            return Response({
                'id': loc.pk,
                'name': loc.name,
                'latitude': float(loc.latitude),
                'longitude': float(loc.longitude),
                'district_name': loc.district.name,
                'region_name': loc.district.region.name,
                'island': loc.district.region.island,
                'size_hectares': float(loc.size_hectares) if loc.size_hectares else None,
                'land_use': loc.land_use,
                'investment_type': loc.investment_type,
                'distance_to_ocean_km': float(loc.distance_to_ocean_km) if loc.distance_to_ocean_km else None,
                'price_per_hectare': float(loc.price_per_hectare) if loc.price_per_hectare else None,
                'price_negotiable': getattr(loc, 'price_negotiable', True),
                'nearby_locations': nearby,
                'description': loc.description,
                'owner': {
                    'name': loc.owner_name,
                    'phone': loc.owner_phone,
                    'email': loc.owner_email,
                    'address': loc.owner_address,
                },
                'zipa': {
                    'phone': loc.zipa_phone,
                    'email': loc.zipa_email,
                    'address': loc.zipa_address,
                },
            })
        except InvestmentLocation.DoesNotExist:
            return Response({'error': 'Location not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def gis_search(request):
    """GIS location search using Nominatim"""
    query = request.query_params.get('q', '')

    if not query:
        return Response({'error': 'Query required'}, status=400)

    import requests
    url = f'https://nominatim.openstreetmap.org/search?q={query}, Zanzibar, Tanzania&format=json&limit=10&countrycodes=tz'

    try:
        response = requests.get(url, headers={'User-Agent': 'SmartGeoApp/1.0'})
        results = response.json()

        data = []
        for r in results:
            data.append({
                'name': r.get('display_name', ''),
                'latitude': float(r.get('lat', 0)),
                'longitude': float(r.get('lon', 0)),
                'type': r.get('type', ''),
            })

        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)