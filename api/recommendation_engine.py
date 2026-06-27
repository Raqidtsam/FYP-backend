from .models import District, EconomicActivity, DistrictActivity, InvestmentSector, Recommendation


class RecommendationEngine:
    """AI-powered recommendation engine for Zanzibar investments"""

    # Map economic activities to suitable investment sectors
    ACTIVITY_TO_SECTOR = {
        'Utalii': ['Hoteli na Malazi', 'Miundombinu ya Utalii', 'Usafiri wa Baharini'],
        'Uvuvi': ['Uvuvi wa Kisasa'],
        'Kilimo': ['Kilimo cha Mwani', 'Viwanda vya Karafuu'],
        'Biashara': ['Biashara ya Jumla'],
        'Ujenzi': ['Miundombinu ya Utalii'],
    }

    # Capital level mapping
    CAPITAL_LEVELS = {
        'High': 0.7,
        'Medium': 0.85,
        'Low': 1.0,
    }

    def generate_recommendations(self, district_id=None):
        """Generate recommendations based on economic activities"""

        districts = District.objects.all()
        if district_id:
            districts = districts.filter(id=district_id)

        # Clear old recommendations
        if district_id:
            Recommendation.objects.filter(district_id=district_id).delete()
        else:
            Recommendation.objects.all().delete()

        new_recommendations = []

        for district in districts:
            district_activities = DistrictActivity.objects.filter(district=district)

            for da in district_activities:
                activity_category = da.activity.category
                dominance = da.dominance

                # Get suitable sectors for this activity
                suitable_sectors = self.ACTIVITY_TO_SECTOR.get(activity_category, [])

                for sector_name in suitable_sectors:
                    try:
                        sector = InvestmentSector.objects.get(name=sector_name)

                        # Calculate base score
                        base_score = self._calculate_base_score(dominance)

                        # Adjust based on capital required matching
                        capital_score = self._calculate_capital_score(
                            sector.capital_required, activity_category
                        )

                        # ROI adjustment
                        roi_score = self._calculate_roi_score(sector.estimated_roi)

                        # Final score (weighted average)
                        final_score = (base_score * 0.5) + (capital_score * 0.3) + (roi_score * 0.2)

                        # Round to whole number
                        final_score = min(100, max(10, round(final_score)))

                        # Generate reason
                        reason = self._generate_reason(
                            district.name, sector.name, activity_category, dominance, final_score
                        )

                        new_recommendations.append(
                            Recommendation(
                                district=district,
                                sector=sector,
                                score=final_score,
                                reason=reason
                            )
                        )
                    except InvestmentSector.DoesNotExist:
                        continue

        # Bulk create recommendations
        Recommendation.objects.bulk_create(new_recommendations)

        return len(new_recommendations)

    def _calculate_base_score(self, dominance):
        """Calculate score based on activity dominance"""
        scores = {'High': 85, 'Medium': 65, 'Low': 45}
        return scores.get(dominance, 40)

    def _calculate_capital_score(self, capital_required, activity_category):
        """Calculate score based on capital matching"""
        ideal_capital = {
            'Utalii': 'High',
            'Uvuvi': 'Medium',
            'Kilimo': 'Low',
            'Biashara': 'Medium',
            'Ujenzi': 'High',
        }

        ideal = ideal_capital.get(activity_category, 'Medium')
        capital_scores = {
            ('High', 'High'): 90,
            ('High', 'Medium'): 70,
            ('High', 'Low'): 50,
            ('Medium', 'Medium'): 90,
            ('Medium', 'High'): 75,
            ('Medium', 'Low'): 65,
            ('Low', 'Low'): 90,
            ('Low', 'Medium'): 70,
            ('Low', 'High'): 50,
        }
        return capital_scores.get((capital_required, ideal), 60)

    def _calculate_roi_score(self, estimated_roi):
        """Calculate score based on ROI range"""
        if not estimated_roi:
            return 60

        try:
            parts = estimated_roi.replace('%', '').split('-')
            if len(parts) == 2:
                avg_roi = (float(parts[0]) + float(parts[1])) / 2
                if avg_roi >= 25:
                    return 95
                elif avg_roi >= 20:
                    return 85
                elif avg_roi >= 15:
                    return 75
                elif avg_roi >= 10:
                    return 65
                else:
                    return 50
        except (ValueError, AttributeError):
            pass
        return 60

    def _generate_reason(self, district_name, sector_name, activity, dominance, score):
        """Generate human-readable reason for recommendation"""

        dominance_text = {
            'High': 'shughuli kuu',
            'Medium': 'shughuli ya wastani',
            'Low': 'shughuli ndogo',
        }

        score_text = ''
        if score >= 80:
            score_text = 'Pendekezo kali'
        elif score >= 60:
            score_text = 'Pendekezo zuri'
        else:
            score_text = 'Pendekezo la wastani'

        return (
            f'{score_text}: {sector_name} inafaa katika {district_name}. '
            f'{activity} ni {dominance_text.get(dominance, "inayopatikana")} '
            f'katika eneo hili.'
        )


# Singleton instance
engine = RecommendationEngine()