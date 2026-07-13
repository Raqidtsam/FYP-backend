from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken
from .models import (
    Region, District, EconomicActivity, DistrictActivity,
    InvestmentSector, Recommendation, User
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


from .models import Message


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
                    # Admin sees all messages (top-level only)
                    return Message.objects.filter(parent__isnull=True)
                else:
                    # User sees their own messages
                    return Message.objects.filter(sender_id=user_id)
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

            # Find admin to send to
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