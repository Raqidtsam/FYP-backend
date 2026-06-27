from django.core.management.base import BaseCommand
from api.models import (
    Region, District, EconomicActivity,
    DistrictActivity, InvestmentSector, Recommendation
)


class Command(BaseCommand):
    help = 'Populate database with Zanzibar data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database...')

        # Clear existing data
        Recommendation.objects.all().delete()
        DistrictActivity.objects.all().delete()
        District.objects.all().delete()
        InvestmentSector.objects.all().delete()
        EconomicActivity.objects.all().delete()
        Region.objects.all().delete()

        # === REGIONS ===
        mjini_magharibi = Region.objects.create(
            name='Mjini Magharibi', island='Unguja',
            latitude=-6.1659, longitude=39.2026
        )
        kaskazini_unguja = Region.objects.create(
            name='Kaskazini Unguja', island='Unguja',
            latitude=-5.9000, longitude=39.3000
        )
        kusini_unguja = Region.objects.create(
            name='Kusini Unguja', island='Unguja',
            latitude=-6.3500, longitude=39.5000
        )
        kaskazini_pemba = Region.objects.create(
            name='Kaskazini Pemba', island='Pemba',
            latitude=-5.0500, longitude=39.7333
        )
        kusini_pemba = Region.objects.create(
            name='Kusini Pemba', island='Pemba',
            latitude=-5.3500, longitude=39.7333
        )

        # === DISTRICTS ===
        mjini = District.objects.create(
            region=mjini_magharibi, name='Mjini',
            latitude=-6.1659, longitude=39.2026
        )
        magharibi = District.objects.create(
            region=mjini_magharibi, name='Magharibi',
            latitude=-6.2000, longitude=39.1800
        )
        kaskazini_a = District.objects.create(
            region=kaskazini_unguja, name='Kaskazini A',
            latitude=-5.9000, longitude=39.3000
        )
        kaskazini_b = District.objects.create(
            region=kaskazini_unguja, name='Kaskazini B',
            latitude=-5.9200, longitude=39.3200
        )
        kati = District.objects.create(
            region=kusini_unguja, name='Kati',
            latitude=-6.2500, longitude=39.4500
        )
        kusini = District.objects.create(
            region=kusini_unguja, name='Kusini',
            latitude=-6.3500, longitude=39.5000
        )
        wete = District.objects.create(
            region=kaskazini_pemba, name='Wete',
            latitude=-5.0500, longitude=39.7333
        )
        micheweni = District.objects.create(
            region=kaskazini_pemba, name='Micheweni',
            latitude=-5.0200, longitude=39.7500
        )
        mkoani = District.objects.create(
            region=kusini_pemba, name='Mkoani',
            latitude=-5.3500, longitude=39.7333
        )
        chake_chake = District.objects.create(
            region=kusini_pemba, name='Chake Chake',
            latitude=-5.2500, longitude=39.7666
        )

        # === ECONOMIC ACTIVITIES ===
        utalii = EconomicActivity.objects.create(
            name='Utalii', category='Utalii',
            description='Hoteli, fukwe, vivutio vya watalii'
        )
        uvuvi = EconomicActivity.objects.create(
            name='Uvuvi', category='Uvuvi',
            description='Uvuvi wa samaki na mazao ya baharini'
        )
        kilimo_mwani = EconomicActivity.objects.create(
            name='Kilimo cha Mwani', category='Kilimo',
            description='Kilimo cha mwani kwa ajili ya bidhaa'
        )
        kilimo_viungo = EconomicActivity.objects.create(
            name='Kilimo cha Viungo', category='Kilimo',
            description='Karafuu, mdalasini, n.k'
        )
        biashara = EconomicActivity.objects.create(
            name='Biashara', category='Biashara',
            description='Biashara ya bidhaa na huduma'
        )
        ujenzi = EconomicActivity.objects.create(
            name='Ujenzi', category='Ujenzi',
            description='Ujenzi wa nyumba na miundombinu'
        )

        # === INVESTMENT SECTORS ===
        hoteli = InvestmentSector.objects.create(
            name='Hoteli na Malazi', capital_required='High',
            estimated_roi='15-25%',
            description='Uwekezaji katika hoteli za kitalii'
        )
        mwani_sector = InvestmentSector.objects.create(
            name='Kilimo cha Mwani', capital_required='Low',
            estimated_roi='20-30%',
            description='Kilimo na usindikaji wa mwani'
        )
        uvuvi_kisasa = InvestmentSector.objects.create(
            name='Uvuvi wa Kisasa', capital_required='Medium',
            estimated_roi='15-20%',
            description='Boti za kisasa na vifaa vya uvuvi'
        )
        viwanda_karafuu = InvestmentSector.objects.create(
            name='Viwanda vya Karafuu', capital_required='Medium',
            estimated_roi='18-25%',
            description='Usindikaji wa karafuu na viungo'
        )
        miundombinu = InvestmentSector.objects.create(
            name='Miundombinu ya Utalii', capital_required='High',
            estimated_roi='10-20%',
            description='Barabara, maji, umeme kwa maeneo ya kitalii'
        )
        biashara_jumla = InvestmentSector.objects.create(
            name='Biashara ya Jumla', capital_required='Medium',
            estimated_roi='12-18%',
            description='Maduka makubwa na masoko'
        )
        usafiri_baharini = InvestmentSector.objects.create(
            name='Usafiri wa Baharini', capital_required='High',
            estimated_roi='15-22%',
            description='Feri na boti za usafiri kati ya visiwa'
        )

        # === DISTRICT ACTIVITIES ===
        activities_data = [
            (mjini, utalii, 'High'),
            (mjini, biashara, 'High'),
            (mjini, uvuvi, 'Medium'),
            (magharibi, utalii, 'Medium'),
            (magharibi, kilimo_mwani, 'Low'),
            (kaskazini_a, utalii, 'High'),
            (kaskazini_a, uvuvi, 'Medium'),
            (kaskazini_b, kilimo_viungo, 'High'),
            (kaskazini_b, uvuvi, 'Low'),
            (kati, kilimo_viungo, 'Medium'),
            (kati, uvuvi, 'Medium'),
            (kusini, kilimo_mwani, 'High'),
            (kusini, uvuvi, 'High'),
            (wete, kilimo_viungo, 'High'),
            (wete, uvuvi, 'Medium'),
            (micheweni, uvuvi, 'High'),
            (micheweni, kilimo_viungo, 'Medium'),
            (mkoani, uvuvi, 'High'),
            (mkoani, kilimo_mwani, 'Medium'),
            (chake_chake, biashara, 'High'),
            (chake_chake, kilimo_viungo, 'High'),
        ]

        for district, activity, dominance in activities_data:
            DistrictActivity.objects.create(
                district=district, activity=activity, dominance=dominance
            )

        # === RECOMMENDATIONS ===
        recommendations_data = [
            (mjini, hoteli, 90, 'Eneo lenye watalii wengi, karibu na Airport na Stone Town'),
            (mjini, biashara_jumla, 85, 'Msongamano mkubwa wa watu na watalii'),
            (mjini, usafiri_baharini, 80, 'Bandari kuu ya Zanzibar, kitovu cha usafiri'),
            (magharibi, hoteli, 75, 'Fukwe nzuri na vivutio vya utalii vingi'),
            (magharibi, mwani_sector, 70, 'Eneo linafaa kwa kilimo cha mwani'),
            (kaskazini_a, hoteli, 88, 'Nungwi na Kendwa - fukwe maarufu duniani'),
            (kaskazini_a, uvuvi_kisasa, 82, 'Eneo la wavuvi wengi, bahari yenye samaki wengi'),
            (kaskazini_b, viwanda_karafuu, 90, 'Eneo maarufu kwa kilimo cha karafuu na viungo'),
            (kaskazini_b, uvuvi_kisasa, 65, 'Uwezekano wa uvuvi katika maeneo ya pwani'),
            (kati, viwanda_karafuu, 75, 'Maeneo ya kilimo cha viungo yapo mengi'),
            (kati, uvuvi_kisasa, 72, 'Pwani ya mashariki ina uwezo wa uvuvi'),
            (kusini, mwani_sector, 92, 'Eneo bora kwa kilimo cha mwani, maji safi na yenye kina kifupi'),
            (kusini, uvuvi_kisasa, 85, 'Uvuvi ni shughuli kuu ya wakazi wa eneo hili'),
            (wete, viwanda_karafuu, 93, 'Wete ni kitovu cha karafuu Pemba, mashamba makubwa yapo'),
            (wete, uvuvi_kisasa, 70, 'Pwani ina uwezo mzuri wa uvuvi'),
            (micheweni, uvuvi_kisasa, 88, 'Wavuvi wengi na samaki wengi baharini'),
            (micheweni, viwanda_karafuu, 78, 'Pia kuna mashamba ya karafuu'),
            (mkoani, uvuvi_kisasa, 86, 'Bandari kuu ya Pemba, uvuvi ni shughuli kuu'),
            (mkoani, mwani_sector, 75, 'Maeneo ya pwani yanafaa kwa mwani'),
            (chake_chake, biashara_jumla, 88, 'Makao makuu ya Pemba, biashara inastawi'),
            (chake_chake, viwanda_karafuu, 85, 'Karibu na mashamba makubwa ya karafuu'),
            (chake_chake, usafiri_baharini, 72, 'Uwanja wa ndege na bandari zipo karibu'),
        ]

        for district, sector, score, reason in recommendations_data:
            Recommendation.objects.create(
                district=district, sector=sector,
                score=score, reason=reason
            )

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))