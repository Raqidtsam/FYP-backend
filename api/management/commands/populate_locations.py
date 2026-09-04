from django.core.management.base import BaseCommand
from api.models import District, InvestmentLocation


class Command(BaseCommand):
    help = 'Populate investment locations'

    def handle(self, *args, **kwargs):
        InvestmentLocation.objects.all().delete()

        # Get districts
        mjini = District.objects.get(name='Mjini')
        kaskazini_a = District.objects.get(name='Kaskazini A')
        kusini = District.objects.get(name='Kusini')

        # Nungwi Investment Zone
        InvestmentLocation.objects.create(
            district=kaskazini_a,
            name='Nungwi Beach Investment Zone',
            latitude=-5.7500,
            longitude=39.3000,
            size_hectares=15.5,
            land_use='Tourism & Hospitality',
            distance_to_ocean_km=0.1,
            nearby_locations='[{"name": "Stone Town", "distance_km": 45}, {"name": "Abeid Amani Karume Airport", "distance_km": 60}]',
            owner_name='Mr. Ali Mohammed',
            owner_phone='+255 777 123 456',
            owner_email='ali.mohammed@example.com',
            owner_address='Nungwi, Kaskazini A, Zanzibar',
            description='Prime beachfront land perfect for hotels and resorts.',
        )

        # Stone Town Commercial
        InvestmentLocation.objects.create(
            district=mjini,
            name='Stone Town Commercial Plot',
            latitude=-6.1659,
            longitude=39.2026,
            size_hectares=2.0,
            land_use='Commercial',
            distance_to_ocean_km=0.2,
            nearby_locations='[{"name": "Zanzibar Port", "distance_km": 1}, {"name": "Darajani Market", "distance_km": 0.5}]',
            owner_name='Ms. Fatma Hassan',
            owner_phone='+255 777 987 654',
            owner_email='fatma.hassan@example.com',
            owner_address='Stone Town, Mjini, Zanzibar',
            description='Ideal for offices, shops, and mixed-use development.',
        )

        # Paje Beachfront
        InvestmentLocation.objects.create(
            district=kusini,
            name='Paje Beachfront Investment',
            latitude=-6.3500,
            longitude=39.5000,
            size_hectares=20.0,
            land_use='Tourism & Residential',
            distance_to_ocean_km=0.05,
            nearby_locations='[{"name": "Jambiani", "distance_km": 5}, {"name": "Kitesurfing Center", "distance_km": 0.3}]',
            owner_name='Mr. Juma Khamis',
            owner_phone='+255 715 555 888',
            owner_email='juma.khamis@example.com',
            owner_address='Paje, Kusini, Zanzibar',
            description='Beautiful beachfront land for resort or villa development.',
        )

        self.stdout.write(self.style.SUCCESS('Investment locations populated!'))