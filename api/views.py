from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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


class EconomicActivityViewSet(viewsets.ModelViewSet):
    queryset = EconomicActivity.objects.all()
    serializer_class = EconomicActivitySerializer


class DistrictActivityViewSet(viewsets.ModelViewSet):
    queryset = DistrictActivity.objects.all()
    serializer_class = DistrictActivitySerializer


class InvestmentSectorViewSet(viewsets.ModelViewSet):
    queryset = InvestmentSector.objects.all()
    serializer_class = InvestmentSectorSerializer


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
