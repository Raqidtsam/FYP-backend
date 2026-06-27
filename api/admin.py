from django.contrib import admin
from .models import (
    Region, District, EconomicActivity, DistrictActivity,
    InvestmentSector, Recommendation, User
)

admin.site.register(Region)
admin.site.register(District)
admin.site.register(EconomicActivity)
admin.site.register(DistrictActivity)
admin.site.register(InvestmentSector)
admin.site.register(Recommendation)
admin.site.register(User)